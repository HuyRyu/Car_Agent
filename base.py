class BaseCrawler():
    def __init__(self, url: str) -> None:
        self.url = url
    
    def get_data(self):
        raise NotImplementedError("Method is not implemented yet.")