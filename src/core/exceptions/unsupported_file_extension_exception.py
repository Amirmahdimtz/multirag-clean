from src.core.exceptions.bad_request_exception import (
    BadRequestException,
)


class UnsupportedFileExtensionException(
    BadRequestException
):
    def __init__(
        self,
        allowed_extensions: list[str],
    ) -> None:
        formatted_extensions = ", ".join(
            f".{extension}"
            for extension in allowed_extensions
        )

        super().__init__(
            message=(
                "Unsupported file extension. "
                "Allowed extensions: "
                f"{formatted_extensions}."
            )
        )
