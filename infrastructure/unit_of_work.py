
from contextlib import contextmanager
from typing import Callable, Dict, Iterator

from account import Repository

from .memory_store import MemoryStore


RepositoryFactory = Callable[[MemoryStore], Repository]


class UnitOfWork:
    """An implementation of the unit of work pattern for a memory store. It
    constructs repositories which are implemented using the store and manages
    the scope of the transaction.

    A UnitOfWork instance is only intended to be used for the duration of a
    single unit of work. Generally it will be used via the WorkManager class.

    """

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
    """A manager for units of work. It can be used as a context manager.

    To manually manage the units of work:
    >>> store = MemoryStore()
    >>> manager = WorkManager(store)
    >>> unit = manager.unit()
    >>> unit.begin()
    ... (do work)
    >>> unit.commit()

    To use it as a context manager:
    >>> with manager.scope() as SCOPE:
    >>>     ...

    """

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
