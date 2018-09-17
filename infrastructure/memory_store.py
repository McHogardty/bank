
import copy
from typing import Any, Callable, Dict, Iterable
from uuid import UUID

StorageRecord = Dict[str, Any]
RecordStore = Dict[UUID, StorageRecord]
SearchPredicate = Callable[[StorageRecord], bool]


class NotFound(Exception):
    pass


class MemoryStore:
    def __init__(self):
        self._records: Dict[str, RecordStore] = {}
        self._changed: Dict[str, RecordStore] = {}
        self._deleted: Dict[str, RecordStore] = {}

    def get(self, record_type: str, key: UUID) -> StorageRecord:
        try:
            return copy.deepcopy(self._changed[record_type][key])
        except KeyError:
            pass

        try:
            return copy.deepcopy(self._records[record_type][key])
        except KeyError:
            raise NotFound

    def find(self,
             record_type: str,
             predicate: SearchPredicate) -> Iterable[StorageRecord]:
        changed_records = self._changed.get(record_type, {})
        existing_records = self._records.get(record_type, {})

        if not changed_records and not existing_records:
            return []

        return (copy.deepcopy(r)
                for r in {**existing_records, **changed_records}.values()
                if predicate(r))

    def add(self,
            record_type: str,
            key: UUID,
            record: StorageRecord) -> None:
        self._changed.setdefault(record_type, {})[key] = copy.deepcopy(record)

    def update(self,
               record_type: str,
               key: UUID,
               record: StorageRecord) -> None:
        self._changed.setdefault(record_type, {})[key] = copy.deepcopy(record)

    def rollback(self) -> None:
        self._changed = {}
        self._deleted = {}

    def commit(self) -> None:
        for k, v in self._changed.items():
            self._records[k].update(v)
