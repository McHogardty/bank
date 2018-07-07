
from uuid import UUID, uuid4


class Entity:
    def __init__(self, id: UUID = None) -> None:
        self.id = id or uuid4()

    def __repr__(self) -> str:
        properties = ['='.join((k, str(v))) for k, v in self.__dict__.items()
                      if k != 'id']
        properties.sort()
        return '{}(id={}{}{})'.format(self.__class__.__name__, self.id,
                                      ', ' if properties else '',
                                      ', '.join(properties))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented

        return self.__class__ == other.__class__ and self.id == other.id
