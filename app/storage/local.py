import os
from app.storage.base import Storage

class LocalDiskStorage(Storage):
    def __init__(self, base_path: str = "storage_data"):
        # This will create a folder named 'storage_data' in your project root
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _full_path(self, path: str) -> str:
        # Joins base path with requested path (e.g. storage_data/documents/xyz.bin)
        return os.path.join(self.base_path, path)

    def save(self, path: str, content: bytes) -> None:
        full_path = self._full_path(path)
        
        # Ensure the sub-directories exist (e.g. creating the project_id folder)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "wb") as f:
            f.write(content)

    def read(self, path: str) -> bytes:
        full_path = self._full_path(path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found at {path}")
            
        with open(full_path, "rb") as f:
            return f.read()

    def delete(self, path: str) -> None:
        full_path = self._full_path(path)
        if os.path.exists(full_path):
            os.remove(full_path)

