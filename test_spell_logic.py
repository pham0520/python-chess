"""
Unit tests for Spell Chess game logic.

Run with:
    pytest test_spell_logic.py -v

These tests verify the Spell Chess rules described in SPELL_CHESS_RULES.md.
Each test creates a fresh SpellChessGame, sets up a position, performs an
action, and checks that the result matches the specification.
"""

import chess
from spell_logic import SpellChessGame, squares_in_3x3, squares_in_jump_range


# ------------------------------------------------------------------ #
#  Demo tests — provided to students as examples                      #
# ------------------------------------------------------------------ #

class TestFreezeTarget:
    """Casting Freeze should mark the opponent's color as frozen."""

    def test_freeze_affects_opponent_not_caster(self):
        game = SpellChessGame()
        # White casts freeze
        game.cast_freeze(chess.E5)
        # The frozen color should be Black (the opponent), not White
        assert game.freeze_effect_color == chess.BLACK


class TestNewGameResetsBoard:
    """Calling new_game() should bring the board back to the starting position."""

    def test_board_resets_after_moves(self):
        game = SpellChessGame()
        game.board.push_san("e4")
        game.new_game()
        assert game.board.fen() == chess.STARTING_FEN


# ------------------------------------------------------------------ #
#  YOUR TESTS GO BELOW                                                #
#  Write tests that check the rules from SPELL_CHESS_RULES.md.        #
#  If a test fails, you've found a bug — document it!                 #
# ------------------------------------------------------------------ #

class TestFreezeInitialState:
    """Freeze bookkeeping should start with default values."""

    def test_freeze_defaults(self):
        game = SpellChessGame()
        assert game.freeze_effect_color is None
        assert game.freeze_effect_squares == set()
        assert game.freeze_effect_plies_left == 0
        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_remaining[chess.BLACK] == 5
        assert game.freeze_cooldown[chess.WHITE] == 0
        assert game.freeze_cooldown[chess.BLACK] == 0
        assert game.spell_casted_this_turn is False

    def test_new_game_resets_freeze_state(self):
        game = SpellChessGame()
        game.cast_freeze(chess.E5)
        game.new_game()
        assert game.freeze_effect_color is None
        assert game.freeze_effect_squares == set()
        assert game.freeze_effect_plies_left == 0
        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_remaining[chess.BLACK] == 5
        assert game.freeze_cooldown[chess.WHITE] == 0
        assert game.freeze_cooldown[chess.BLACK] == 0


class TestFreezeArea:
    """Freeze area should be a 3x3 centered on the selected square."""

    def test_squares_in_3x3_center_square_included(self):
        area = squares_in_3x3(chess.E5)
        assert chess.E5 in area

    def test_squares_in_3x3_corner_has_four_squares(self):
        area = squares_in_3x3(chess.A1)
        assert area == {chess.A1, chess.A2, chess.B1, chess.B2}


class TestFreezeCastRules:
    """Freeze casting should follow charges, cooldown, and per-turn limits."""

    def test_freeze_decreases_current_player_charges(self):
        game = SpellChessGame()
        before = game.freeze_remaining[chess.WHITE]
        game.cast_freeze(chess.E5)
        assert game.freeze_remaining[chess.WHITE] == before - 1

    def test_freeze_prevents_second_cast_same_turn(self):
        game = SpellChessGame()
        assert game.cast_freeze(chess.E5) is True
        assert game.cast_freeze(chess.D4) is False

    def test_freeze_fails_with_no_charges(self):
        game = SpellChessGame()
        game.freeze_remaining[chess.WHITE] = 0
        assert game.cast_freeze(chess.E5) is False


class TestFreezeMoveBlocking:
    """Frozen origin squares should be filtered from legal moves."""

    def test_frozen_piece_origins_are_blocked(self):
        game = SpellChessGame()
        game.cast_freeze(chess.E7)
        game.board.turn = chess.BLACK
        legal_moves = game.get_legal_moves()
        assert chess.Move.from_uci("e7e5") not in legal_moves
        assert chess.Move.from_uci("e7e6") not in legal_moves


class TestFreezeEffectDuration:
    """Freeze should last exactly one opponent turn."""

    def test_freeze_effect_expires_after_opponent_moves_once(self):
        game = SpellChessGame()
        assert game.cast_freeze(chess.E7) is True
        assert game.freeze_effect_color == chess.BLACK

        # White makes a move; freeze should still affect Black.
        game.make_move(chess.E2, chess.E4)
        assert game.freeze_effect_color == chess.BLACK

        # Black makes one move; freeze should now expire.
        game.make_move(chess.G8, chess.F6)
        assert game.freeze_effect_color is None

    def test_freeze_cooldown_decrements_on_caster_turn_start(self):
        game = SpellChessGame()
        game.freeze_cooldown[chess.WHITE] = 3
        game.board.turn = chess.WHITE
        game.on_turn_start()
        assert game.freeze_cooldown[chess.WHITE] == 2


class TestFrozenPieceChecks:
    """Frozen pieces still give check and block squares."""

    def test_frozen_piece_still_gives_check(self):
        """A frozen piece must still be defended against if it gives check."""
        game = SpellChessGame()
        # Set up a position where White knight on E5 gives check to Black king on D7
        game.board.clear()
        game.board.set_piece_at(chess.D7, chess.Piece(chess.KING, chess.BLACK))
        game.board.set_piece_at(chess.E5, chess.Piece(chess.KNIGHT, chess.WHITE))
        game.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        game.board.turn = chess.WHITE

        # White freezes the knight; Black still in check
        game.cast_freeze(chess.E5)
        game.board.turn = chess.BLACK
        
        # Black king must still be in check
        assert game.board.is_check()