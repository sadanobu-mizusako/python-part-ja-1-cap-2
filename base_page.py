from abc import ABC, abstractmethod

class BaseDisplay(ABC):
    """
    ページの挙動を定める要素。前処理、可視化、後処理の3つで構成する
    """
    def __init__(self) -> None:
        super().__init__()
        self.preprocess()
        self.show()
        self.postprocess()

    @abstractmethod
    def preprocess():
        pass

    @abstractmethod
    def show():
        pass

    @abstractmethod
    def postprocess():
        pass