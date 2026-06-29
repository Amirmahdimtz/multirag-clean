from uuid import UUID


class ChatBusiness:
    def __init__(
        self,
        chat_session_business,
        chat_message_business,
        rag_system_business,
        chat_llm,
    ) -> None:
        self.chat_session_business = chat_session_business
        self.chat_message_business = chat_message_business
        self.rag_system_business = rag_system_business
        self.chat_llm = chat_llm

    async def create_session(
        self,
        user_id: UUID,
        name: str,
        llm_type: str = "simple",
    ):
        return await self.chat_session_business.create_session(
            user_id=user_id,
            name=name,
            llm_type=llm_type,
        )

    async def get_user_sessions(
        self,
        user_id: UUID,
    ):
        return await self.chat_session_business.get_user_sessions(
            user_id=user_id,
        )

    async def send_message(
        self,
        session_id: UUID,
        question: str,
        rag_system_id: UUID | None = None,
    ) -> str:
        await self.chat_session_business.get_by_id(session_id)

        history = await self.chat_message_business.get_session_messages(
            session_id=session_id,
        )

        contexts = []

        if rag_system_id:
            rag_results = await self.rag_system_business.search(
                rag_system_id=rag_system_id,
                query=question,
                limit=5,
            )

            contexts = [
                result.document.content
                for result in rag_results
            ]

        answer = await self.chat_llm.generate(
            question=question,
            contexts=contexts,
            history_messages=history,
        )

        await self.chat_message_business.add_message(
            session_id=session_id,
            role="user",
            content=question,
        )

        await self.chat_message_business.add_message(
            session_id=session_id,
            role="assistant",
            content=answer,
        )

        return answer
