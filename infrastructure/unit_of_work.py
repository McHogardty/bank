
from contextlib import contextmanager
from typing import Callable, Dict, Iterator

from account import Repository

from .memory_store import MemoryStore


RepositoryFactory = Callable[[MemoryStore], Repository]


class UnitOfWork:
    def __init__(self, store):
        self._factories: Dict[RepositoryFactory, Repository] = {}
        self._store: MemoryStore = store

    def get(self, factory: RepositoryFactory) -> Repository:
        try:
            return self._factories[factory]
        except KeyError:
            self._factories[factory] = repo = factory(self._store)
            return repo

    def begin(self) -> None:
        self._store.begin()

    def commit(self) -> None:
        self._store.commit()

    def rollback(self) -> None:
        self._store.rollback()


class WorkManager:
    def __init__(self, store):
        self._store = store

    def unit(self) -> UnitOfWork:
        return UnitOfWork(self._store)

    @contextmanager
    def scope(self) -> Iterator[UnitOfWork]:
        current_unit = UnitOfWork(self._store)

        current_unit.begin()
        try:
            yield current_unit
        except Exception:
            current_unit.rollback()
            raise
        else:
            current_unit.commit()
