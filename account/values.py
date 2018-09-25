
from __future__ import annotations

from decimal import Decimal


class AUD(Decimal):
    def __repr__(self) -> str:
        return "AUD({!r})".format(super(AUD, self).__str__())

    def __str__(self) -> str:
        if self < 0:
            return "-${}".format(-self)
        else:
            return "${}".format(self)

    def __deepcopy__(self, memo=None) -> AUD:  # noqa
        return AUD(super(AUD, self).__deepcopy__(memo))

    def __add__(self, other: object) -> AUD:  # noqa
        try:
            return AUD(super(AUD, self).__add__(AUD(other)))
        except Exception:
            return NotImplemented

    def __radd__(self, other: object) -> AUD:  # noqa
        return self.__add__(other)

    def __sub__(self, other: object) -> AUD:  # noqa
        try:
            return AUD(super(AUD, self).__sub__(AUD(other)))
        except Exception:
            return NotImplemented


class CardNumber:
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return "CardNumber({!r})".format(self.value)

    def __str__(self) -> str:
        return " ".join(self.value[i:i + 4]
                        for i in range(0, len(self.value), 4))

    def __deepcopy__(self, memo=None) -> CardNumber:  # noqa
        return CardNumber(self.value)

    def __eq__(self, other) -> bool:
        return isinstance(other, CardNumber) and other.value == self.value
