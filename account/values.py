
from __future__ import annotations

from decimal import Decimal
from typing import TypeVar

Self = TypeVar('Self')


class AUD(Decimal):
    def __repr__(self) -> str:
        return "AUD({!r})".format(super(AUD, self).__str__())

    def __str__(self) -> str:
        return "${}".format(self)
