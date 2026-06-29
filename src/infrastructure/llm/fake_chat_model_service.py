from src.core.llm.base_chat_model_service import BaseChatModelService


class FakeChatModelService(BaseChatModelService):
    async def generate(self, prompt: str) -> str:
        context_marker = "CONTEXT:"
        question_marker = "QUESTION:"

        if context_marker in prompt and question_marker in prompt:
            question = prompt.split(question_marker, 1)[1].strip()

            return (
                "این پاسخ توسط FakeChatModelService تولید شده است.\n\n"
                "بر اساس متن‌های بازیابی‌شده، پاسخ پیشنهادی برای سؤال شما این است:\n"
                f"{question}\n\n"
                "نکته: در جلسه‌های بعدی این سرویس را با LLM واقعی مثل Ollama جایگزین می‌کنیم."
            )

        return (
            "این پاسخ ساده توسط FakeChatModelService تولید شده است.\n"
            f"Prompt received:\n{prompt[:500]}"
        )
