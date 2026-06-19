import pytest

from backend.domain.tiles import Suit, SuitType, MeldType
from backend.utils.errors import DiscardError, InvalidActionError


class TestDiscardError:
    def test_is_exception(self):
        assert issubclass(DiscardError, Exception)

    def test_stores_message_and_tile(self):
        tile = Suit(SuitType.DOT, 5)
        err = DiscardError("cannot discard", tile)
        assert err.tile == tile
        assert "cannot discard" in str(err)

    def test_can_be_caught(self):
        try:
            raise DiscardError("msg", Suit(SuitType.DOT, 1))
        except DiscardError as e:
            assert e.tile == Suit(SuitType.DOT, 1)

    def test_can_be_caught_as_exception(self):
        try:
            raise DiscardError("msg", Suit(SuitType.DOT, 1))
        except Exception as e:
            assert isinstance(e, DiscardError)


class TestInvalidActionError:
    def test_is_exception(self):
        assert issubclass(InvalidActionError, Exception)

    def test_stores_message_action_and_tile(self):
        tile = Suit(SuitType.DOT, 5)
        err = InvalidActionError("cannot pong", MeldType.PONG, tile)
        assert err.action == MeldType.PONG
        assert err.tile == tile
        assert "cannot pong" in str(err)

    def test_can_be_caught(self):
        try:
            raise InvalidActionError("cannot chi", MeldType.CHI, Suit(SuitType.DOT, 1))
        except InvalidActionError as e:
            assert e.action == MeldType.CHI
            assert e.tile == Suit(SuitType.DOT, 1)

    def test_can_be_caught_as_exception(self):
        try:
            raise InvalidActionError(
                "cannot gang", MeldType.GANG, Suit(SuitType.DOT, 1)
            )
        except Exception as e:
            assert isinstance(e, InvalidActionError)
