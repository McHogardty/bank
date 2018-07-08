
from __future__ import annotations

from decimal import Decimal
from typing import TypeVar

Self = TypeVar('Self')


class AUD(Decimal):
    def __repr__(self) -> str:
        return "AUD({!r})".format(super(AUD, self).__str__())

    def __str__(self) -> str:
        return "${}".format(self)

    def __add__(self, other: object) -> AUD:  # noqa
        if not isinstance(other, AUD):
            return NotImplemented

        return AUD(super(AUD, self).__add__(other))

    def __sub__(self, other: object) -> AUD:  # noqa
        if not isinstance(other, AUD):
            return NotImplemented

        return AUD(super(AUD, self).__sub__(other))
