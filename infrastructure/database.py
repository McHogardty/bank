
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict
from uuid import UUID

_database: Dict[str, Dict[UUID, dict]] = {}


class AlreadyExists(Exception):
    pass


class NoMatchingRecord(Exception):
    pass


class Database:
    @classmethod
    def insert(cls, model_name: str, record: Dict[str, Any]) -> None:
        if cls.exists(model_name, record['id']):
            raise AlreadyExists('Cannot insert over an existing ID.')

        cls.write_record(model_name, record)

    @classmethod
    def update(cls, model_name: str, record: Dict[str, Any]) -> None:
        if not cls.exists(model_name, record['id']):
            raise NoMatchingRecord('Cannot update non-existent record.')

        cls.write_record(model_name, record)

    @classmethod
    def get(cls, model_name: str, model_id: UUID) -> Dict[str, Any]:
        if not cls.exists(model_name, model_id):
            raise NoMatchingRecord('No record found.')

        return deepcopy(_database[model_name][model_id])

    @classmethod
    def exists(cls, model_name: str, model_id: UUID) -> bool:
        return model_id in _database.get(model_name, {})

    @classmethod
    def write_record(cls, model_name: str, record: Dict[str, Any]) -> None:
        records = _database.setdefault(model_name, {})
        record = deepcopy(record)
        records[record['id']] = record
