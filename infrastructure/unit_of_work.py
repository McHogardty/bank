
from contextlib import contextmanager
from copy import deepcopy
from uuid import UUID

from .database import Database, Record


class UnitOfWork:
    def __init__(self):
        self._new_records = []
        self._dirty_records = []
        self._deleted_records = []

    def add(self, model_name: str, model_record: Record) -> None:
        self._new_records.append((model_name, deepcopy(model_record)))

    def mark_dirty(self, model_name: str, model_record: Record) -> None:
        model_index = None

        for i in range(len(self._dirty_records)):
            m, record = self._dirty_records[i]
            if m == model_name and record['id'] == model_record['id']:
                model_index = i
                break

        if model_index is not None:
            self._dirty_records[model_index] = (model_name, model_record)
        else:
            self._dirty_records.append((model_name, model_record))

    def delete(self, model_name: str, model_id: UUID) -> None:
        self._deleted_records.append((model_name, model_id))

    def commit(self):
        self._save_records()

    def rollback(self):
        self._new_records = []
        self._dirty_records = []
        self._deleted_records = []

    def _save_records(self):
        try:
            for model_name, model_id in self._deleted_records:
                Database.delete(model_name, model_id)

            for model_name, model_record in self._new_records:
                Database.insert(model_name, model_record)

            for model_name, model_record in self._dirty_records:
                Database.update(model_name, model_record)
        finally:
            self._new_records = []
            self._dirty_records = []
            self._deleted_records = []


class WorkManager:
    def __init__(self):
        self._current_unit = None

    def unit(self):
        return UnitOfWork()

    @contextmanager
    def scope(self):
        self._current_unit = self.unit()
        try:
            yield self._current_unit
        except Exception:
            self._current_unit.rollback()
            raise
        else:
            self._current_unit.commit()
        finally:
            self._current_unit = None

    def add(self, model_name: str, model_record: Record) -> None:
        self._current_unit.add(model_name, model_record)

    def mark_dirty(self, model_name: str, model_record: Record) -> None:
        self._current_unit.mark_dirty(model_name, model_record)

    def delete(self, model_name: str, model_id: UUID) -> None:
        self._current_unit.delete(model_name, model_id)
