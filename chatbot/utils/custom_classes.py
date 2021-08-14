from typing import Any, Optional

class SafeDict(dict):
    def __getitem__(self, key: str) -> Any:
        return self.get(key, self._holder)


class SafeDictFabric(dict):

    def __new__(cls, holder: Optional[Any] = None) -> dict:

        adict = SafeDict()
        adict._holder = holder

        return adict
