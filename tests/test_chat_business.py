import unittest
from types import SimpleNamespace
from uuid import uuid4

from src.core.chat.chat_business import ChatBusiness
from src.core.exceptions.bad_request_exception import BadRequestException
from src.core.exceptions.forbidden_exception import ForbiddenException
from src.domain.enums.llm_type import LLMType
from src.domain.enums.message_role import MessageRole
from src.domain.models.chat_message import ChatMessage


class FakeChatSessionBusiness:
    def __init__(self, session=None) -> None:
        self.session = session
        self.created = None
        self.updated = False
        self.deleted = False

    async def create_session(self, **kwargs):
        self.created = kwargs
        return SimpleNamespace(id=uuid4(), **kwargs)

    async def get_user_sessions(self, user_id):
        return [self.session] if self.session is not None else []

    async def get_by_id(self, session_id):
        return self.session

    async def update_last_active(self, session_id):
        self.updated = True
        return self.session

    async def delete_session(self, session_id):
        self.deleted = True


class FakeChatMessageBusiness:
    def __init__(self, messages=None) -> None:
        self.messages = list(messages or [])
        self.added = []
        self.deleted = False

    async def add_message(self, session_id, role, content):
        self.added.append((session_id, role, content))

    async def get_session_messages(self, session_id):
        return self.messages

    async def delete_session_messages(self, session_id):
        self.deleted = True


class FakeRAGAccessBusiness:
    def __init__(self) -> None:
        self.checked = []

    async def ensure_user_has_access(self, user_id, rag_system_id):
        self.checked.append((user_id, rag_system_id))


class FakeUserDatasetBusiness:
    def __init__(self) -> None:
        self.checked = []
        self.searches = []

    async def ensure_user_owns_dataset(self, user_id, dataset_id):
        self.checked.append((user_id, dataset_id))

    async def search_user_dataset(
        self,
        user_id,
        dataset_id,
        query,
    ):
        self.searches.append((user_id, dataset_id, query))
        return []


class FakeRAGSystemBusiness:
    def __init__(self) -> None:
        self.searches = []

    async def search(self, rag_system_id, query):
        self.searches.append((rag_system_id, query))
        return []


class FakeStreamingLLM:
    async def stream(self, question, contexts):
        self.question = question
        self.contexts = contexts
        for token in ("hello", " ", "world"):
            yield token


class FakeLLMFactory:
    def __init__(self) -> None:
        self.simple = FakeStreamingLLM()
        self.rag = FakeStreamingLLM()
        self.user_rag = FakeStreamingLLM()

    def create_simple_llm(self):
        return self.simple

    def create_rag_llm(self):
        return self.rag

    def create_user_rag_llm(self):
        return self.user_rag


class FakeHistoryService:
    def build_history_text(self, messages):
        return "\n".join(
            f"{message.role.value.upper()}: {message.content}"
            for message in messages
        )


class ChatBusinessTests(unittest.IsolatedAsyncioTestCase):
    def build_business(self, session=None, messages=None):
        sessions = FakeChatSessionBusiness(session=session)
        chat_messages = FakeChatMessageBusiness(messages=messages)
        rag_access = FakeRAGAccessBusiness()
        user_datasets = FakeUserDatasetBusiness()
        rag_systems = FakeRAGSystemBusiness()
        llms = FakeLLMFactory()

        business = ChatBusiness(
            chat_session_business=sessions,
            chat_message_business=chat_messages,
            rag_system_business=rag_systems,
            rag_access_business=rag_access,
            user_dataset_business=user_datasets,
            llm_factory=llms,
            chat_history_service=FakeHistoryService(),
        )

        return (
            business,
            sessions,
            chat_messages,
            rag_access,
            user_datasets,
            rag_systems,
            llms,
        )

    async def test_simple_session_rejects_rag_resources(self) -> None:
        business, *_ = self.build_business()

        with self.assertRaises(BadRequestException):
            await business.create_session(
                user_id=uuid4(),
                name="simple",
                llm_type="simple",
                rag_system_id=uuid4(),
            )

    async def test_rag_session_requires_access_before_creation(self) -> None:
        user_id = uuid4()
        rag_system_id = uuid4()
        (
            business,
            sessions,
            _,
            rag_access,
            *_,
        ) = self.build_business()

        await business.create_session(
            user_id=user_id,
            name="rag",
            llm_type="rag",
            rag_system_id=rag_system_id,
        )

        self.assertEqual(
            [(user_id, rag_system_id)],
            rag_access.checked,
        )
        self.assertEqual(
            LLMType.RAG,
            sessions.created["llm_type"],
        )

    async def test_user_rag_session_checks_dataset_ownership(self) -> None:
        user_id = uuid4()
        dataset_id = uuid4()
        (
            business,
            sessions,
            _,
            _,
            user_datasets,
            *_,
        ) = self.build_business()

        await business.create_session(
            user_id=user_id,
            name="personal",
            llm_type="user_rag",
            user_dataset_id=dataset_id,
        )

        self.assertEqual(
            [(user_id, dataset_id)],
            user_datasets.checked,
        )
        self.assertEqual(
            LLMType.USER_RAG,
            sessions.created["llm_type"],
        )

    async def test_delete_session_rejects_non_owner(self) -> None:
        owner_id = uuid4()
        session = SimpleNamespace(
            id=uuid4(),
            user_id=owner_id,
            llm_type=LLMType.SIMPLE,
            rag_system_id=None,
            user_dataset_id=None,
        )
        business, sessions, messages, *_ = self.build_business(
            session=session
        )

        with self.assertRaises(ForbiddenException):
            await business.delete_session(
                user_id=uuid4(),
                session_id=session.id,
            )

        self.assertFalse(messages.deleted)
        self.assertFalse(sessions.deleted)

    async def test_simple_stream_persists_messages_and_activity(self) -> None:
        session_id = uuid4()
        user_id = uuid4()
        session = SimpleNamespace(
            id=session_id,
            user_id=user_id,
            llm_type=LLMType.SIMPLE,
            rag_system_id=None,
            user_dataset_id=None,
        )
        previous = ChatMessage(
            session_id=session_id,
            role=MessageRole.USER,
            content="previous question",
        )
        (
            business,
            sessions,
            messages,
            _,
            _,
            _,
            llms,
        ) = self.build_business(
            session=session,
            messages=[previous],
        )

        tokens = []
        async for token in business.stream_message(
            session_id=session_id,
            question="current question",
        ):
            tokens.append(token)

        self.assertEqual("hello world", "".join(tokens))
        self.assertEqual(
            [
                (session_id, "user", "current question"),
                (session_id, "assistant", "hello world"),
            ],
            messages.added,
        )
        self.assertTrue(sessions.updated)
        self.assertIn(
            "USER: previous question",
            llms.simple.question,
        )
        self.assertIn(
            "CURRENT QUESTION:\ncurrent question",
            llms.simple.question,
        )
        self.assertEqual([], llms.simple.contexts)


if __name__ == "__main__":
    unittest.main()
