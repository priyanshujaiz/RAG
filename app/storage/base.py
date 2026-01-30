from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, path: str, content: bytes) -> None:
        """
        Persist bytes to a specific path.
        Overwrites if exists.
        """
        pass

    @abstractmethod
    def read(self, path: str) -> bytes:
        """
        Retrieve bytes from a specific path.
        Raises error if not found.
        """
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        """
        Remove the file at the specific path.
        """
        pass