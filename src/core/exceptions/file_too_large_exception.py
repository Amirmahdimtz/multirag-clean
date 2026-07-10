from src.core.exceptions.bad_request_exception import (
    BadRequestException,
)


class FileTooLargeException(
    BadRequestException
):
    def __init__(
        self,
        max_file_size_mb: float,
    ) -> None:
        super().__init__(
            message=(
                "File size exceeds "
                "the allowed limit. "
                "Maximum file size: "
                f"{max_file_size_mb:g} MB."
            )
        )
