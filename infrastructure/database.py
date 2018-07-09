
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict, List
from uuid import UUID

Record = Dict[str, Any]

_database: Dict[str, Dict[UUID, Record]] = {}


class AlreadyExists(Exception):
    pass


class NoMatchingRecord(Exception):
    pass


class Database:
    @classmethod
    def insert(cls, model_name: str, record: Record) -> None:
        if cls.exists(model_name, record['id']):
            raise AlreadyExists('Cannot insert over an existing ID.')

        cls.write_record(model_name, record)

    @classmethod
    def update(cls, model_name: str, record: Record) -> None:
        if not cls.exists(model_name, record['id']):
            raise NoMatchingRecord('Cannot update non-existent record.')

        cls.write_record(model_name, record)

    @classmethod
    def get(cls, model_name: str, model_id: UUID) -> Record:
        if not cls.exists(model_name, model_id):
            raise NoMatchingRecord('No record found.')

        return deepcopy(_database[model_name][model_id])

    @classmethod
    def exists(cls, model_name: str, model_id: UUID) -> bool:
        return model_id in _database.get(model_name, {})

    @classmethod
    def find(cls, model_name: str,
             predicate: Callable[[Record], bool] = lambda m: True) -> List[Record]:  # noqa
        return [deepcopy(r)
                for r in _database.get(model_name, {}).values()
                if predicate(r)]

    @classmethod
    def delete(cls, model_name: str, model_id: UUID) -> None:
        _database.get(model_name, {}).pop(model_id, None)

    @classmethod
    def write_record(cls, model_name: str, record: Record) -> None:
        records = _database.setdefault(model_name, {})
        record = deepcopy(record)
        records[record['id']] = record
