from src.host.host_collection import WebHostCollection


class App:
    def start_up(self) -> None:
        WebHostCollection.main()
