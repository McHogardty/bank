
from uuid import UUID

from .base import Entity
from .values import CardNumber


class Card(Entity):
    def __init__(self, id: UUID = None, number: CardNumber = None) -> None:
        super(Card, self).__init__(id=id)

        self.number = number
