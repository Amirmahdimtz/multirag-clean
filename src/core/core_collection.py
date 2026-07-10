from dependency_injector import (
    containers,
    providers,
)

from src.core.chat.chat_business import (
    ChatBusiness,
)
from src.core.chat.chat_history_service import (
    ChatHistoryService,
)
from src.core.chat.chat_message_business import (
    ChatMessageBusiness,
)
from src.core.chat.chat_session_business import (
    ChatSessionBusiness,
)
from src.core.dataset.dataset_business import (
    DatasetBusiness,
)
from src.core.dataset.user_dataset_business import (
    UserDatasetBusiness,
)
from src.core.llm.llm_factory import (
    LLMFactory,
)
from src.core.rag_access.rag_access_business import (
    RAGAccessBusiness,
)
from src.core.rag_system.rag_system_business import (
    RAGSystemBusiness,
)
from src.core.security.api_key_auth_service import (
    ApiKeyAuthService,
)
from src.core.user.user_business import (
    UserBusiness,
)
from src.infrastructure.infrastructure_collection import (
    InfrastructureCollection,
)


class CoreCollection(
    containers.DeclarativeContainer
):
    user_business = providers.Factory(
        UserBusiness,

        user_repository=(
            InfrastructureCollection
            .user_repository
        ),
    )

    llm_factory = providers.Factory(
        LLMFactory,

        chat_model_service=(
            InfrastructureCollection
            .chat_model_service
        ),
    )

    dataset_business = providers.Factory(
        DatasetBusiness,

        dataset_repository=(
            InfrastructureCollection
            .dataset_repository
        ),

        file_storage_service=(
            InfrastructureCollection
            .file_storage_service
        ),

        document_processing_service=(
            InfrastructureCollection
            .document_processing_service
        ),

        embedding_service=(
            InfrastructureCollection
            .embedding_service
        ),

        vector_store_service=(
            InfrastructureCollection
            .vector_store_service
        ),

        allowed_extensions=(
            InfrastructureCollection
            .config_reader
            .provided
            .require
            .call(
                "uploads.allowed_extensions"
            )
        ),

        max_file_size_mb=(
            InfrastructureCollection
            .config_reader
            .provided
            .require
            .call(
                "uploads.max_file_size_mb"
            )
        ),

        default_k_retrieval=(
            InfrastructureCollection
            .config_reader
            .provided
            .require
            .call(
                "rag.k_retrieval"
            )
        ),

        default_score_threshold=(
            InfrastructureCollection
            .config_reader
            .provided
            .get
            .call(
                "rag.score_threshold",
                None,
            )
        ),
    )

    user_dataset_business = (
        providers.Factory(
            UserDatasetBusiness,

            dataset_business=(
                dataset_business
            ),
        )
    )

    api_key_auth_service = (
        providers.Factory(
            ApiKeyAuthService,

            enabled=(
                InfrastructureCollection
                .config_reader
                .provided
                .get
                .call(
                    "security.enabled",
                    False,
                )
            ),

            admin_api_keys=(
                InfrastructureCollection
                .config_reader
                .provided
                .get
                .call(
                    "security.admin_api_keys",
                    [],
                )
            ),

            user_api_keys=(
                InfrastructureCollection
                .config_reader
                .provided
                .get
                .call(
                    "security.user_api_keys",
                    [],
                )
            ),
        )
    )

    rag_system_business = (
        providers.Factory(
            RAGSystemBusiness,

            rag_system_repository=(
                InfrastructureCollection
                .rag_system_repository
            ),

            dataset_repository=(
                InfrastructureCollection
                .dataset_repository
            ),

            embedding_service=(
                InfrastructureCollection
                .embedding_service
            ),

            vector_store_service=(
                InfrastructureCollection
                .vector_store_service
            ),

            default_k_retrieval=(
                InfrastructureCollection
                .config_reader
                .provided
                .require
                .call(
                    "rag.k_retrieval"
                )
            ),

            default_score_threshold=(
                InfrastructureCollection
                .config_reader
                .provided
                .get
                .call(
                    "rag.score_threshold",
                    None,
                )
            ),

            llm_factory=llm_factory,
        )
    )

    rag_access_business = (
        providers.Factory(
            RAGAccessBusiness,

            rag_access_repository=(
                InfrastructureCollection
                .rag_access_repository
            ),

            user_repository=(
                InfrastructureCollection
                .user_repository
            ),

            rag_system_repository=(
                InfrastructureCollection
                .rag_system_repository
            ),
        )
    )

    chat_session_business = (
        providers.Factory(
            ChatSessionBusiness,

            chat_session_repository=(
                InfrastructureCollection
                .chat_session_repository
            ),
        )
    )

    chat_message_business = (
        providers.Factory(
            ChatMessageBusiness,

            chat_message_repository=(
                InfrastructureCollection
                .chat_message_repository
            ),
        )
    )

    chat_history_service = (
        providers.Singleton(
            ChatHistoryService,
        )
    )

    chat_business = providers.Factory(
        ChatBusiness,

        chat_session_business=(
            chat_session_business
        ),

        chat_message_business=(
            chat_message_business
        ),

        rag_system_business=(
            rag_system_business
        ),

        rag_access_business=(
            rag_access_business
        ),

        user_dataset_business=(
            user_dataset_business
        ),

        llm_factory=llm_factory,

        chat_history_service=(
            chat_history_service
        ),
    )
