
import copy
from typing import Any, Callable, Dict, Iterator, Optional
from uuid import UUID


# Define some types.
StorageRecord = Dict[str, Any]
Table = Dict[UUID, StorageRecord]
Store = Dict[str, Table]
SearchPredicate = Callable[[StorageRecord], bool]


class NotFound(Exception):
    """Raised when no records are found."""
    pass


class MemoryStore:
    """A simple implementation of an in-memory store with very simple
    transactions.

    """

    def __init__(self):
        self._records: Store = {}
        self._changed: Optional[Store] = None

    def get(self, record_type: str, key: UUID) -> StorageRecord:
        if self._changed:
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
             predicate: SearchPredicate) -> Iterator[StorageRecord]:
        changed_records: Table = {}
        if self._changed is not None:
            changed_records = self._changed.get(record_type, {})
        existing_records = self._records.get(record_type, {})

        if not changed_records and not existing_records:
            return iter([])

        return (copy.deepcopy(r)
                for r in {**existing_records, **changed_records}.values()
                if predicate(r))

    def add(self,
            record_type: str,
            key: UUID,
            record: StorageRecord) -> None:
        record = copy.deepcopy(record)
        if self._changed is not None:
            self._changed.setdefault(record_type, {})[key] = record
        else:
            self._records.setdefault(record_type, {})[key] = record

    def update(self,
               record_type: str,
               key: UUID,
               record: StorageRecord) -> None:
        record = copy.deepcopy(record)
        if self._changed is not None:
            self._changed.setdefault(record_type, {})[key] = record
        else:
            self._records.setdefault(record_type, {})[key] = record

    def begin(self) -> None:
        self._changed = {}

    def rollback(self) -> None:
        self._changed = None

    def commit(self) -> None:
        if self._changed is not None:
            for k, v in self._changed.items():
                self._records.setdefault(k, {}).update(v)

        self._changed = None
