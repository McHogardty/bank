
from __future__ import annotations

from decimal import Decimal


class AUD(Decimal):
    def __repr__(self) -> str:
        return "AUD({!r})".format(super(AUD, self).__str__())

    def __str__(self) -> str:
        return "${}".format(self)

    def __deepcopy__(self, memo=None) -> AUD:  # noqa
        return AUD(super(AUD, self).__deepcopy__(memo))

    def __add__(self, other: object) -> AUD:  # noqa
        if not isinstance(other, AUD):
            return NotImplemented

        return AUD(super(AUD, self).__add__(other))

    def __sub__(self, other: object) -> AUD:  # noqa
        if not isinstance(other, AUD):
            return NotImplemented

        return AUD(super(AUD, self).__sub__(other))
