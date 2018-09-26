
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID, uuid4


class Entity:
    """A base class for an Entity. Gives a default UUID by default and defines
    some of the default behaviour.

    """

    def __init__(self, id: UUID = None) -> None:
        self.id = id or uuid4()

    def __repr__(self) -> str:
        properties = ['='.join((k, repr(v))) for k, v in self.__dict__.items()
                      if k != 'id']
        properties.sort()
        return '{}(id={}{}{})'.format(self.__class__.__name__, self.id,
                                      ', ' if properties else '',
                                      ', '.join(properties))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented

        return type(self) == type(other) and self.id == other.id


# Represents an Entity for the purposes of defining our Repository generic
# type.
E = TypeVar('E')


class Repository(Generic[E], metaclass=ABCMeta):
    """A Generic repository class defining the methods which are expected to be
    found in every entity repository.

    """

    @abstractmethod
    def get(self, id: UUID) -> E:
        """Find an entity by its ID.

        Takes one argument:
        - id: The ID of the entity.

        Returns an instance of the entity.

        """

        pass

    @abstractmethod
    def add(self, entity: E) -> None:
        """Add a new entity.

        Takes one argument:
        - entity: The entity instance to add.

        """

        pass

    @abstractmethod
    def update(self, entity: E) -> None:
        """Update an entity with modifications.

        Takes one argument:
        - entity: The entity to add.

        """

        pass
