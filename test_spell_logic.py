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

class TestJumpSpellIntialState:
    """ Test that the Jump spell behaves according to the rules. """
    def test_jump_defaults(self):
        game = SpellChessGame()
        game.new_game()
        
        assert game.jump_remaining[chess.WHITE] == 3
        assert game.jump_remaining[chess.BLACK] == 3
        
        assert game.jump_cooldown[chess.WHITE] == 0
        assert game.jump_cooldown[chess.BLACK] == 0
        assert game.jump_casted_this_turn == False 
class TestJumpCastRules:
    
    def test_jump_decreases_current_player_charge(self):
        game = SpellChessGame()
        before = game.jump_remaining[chess.WHITE]
        assert game.cast_jump(chess.A2, chess.A3) == True
        assert game.jump_remaining[chess.WHITE] == before - 1
    
    
    def test_jump_prevents_second_cast_same_turn(self):
        game = SpellChessGame()
        assert game.cast_jump(chess.A2, chess.A3) == True 
        assert game.cast_jump(chess.C2, chess.C3) == False 
    
    
    def test_jump_fails_with_no_charges(self):
        game = SpellChessGame()
        game.jump_remaining[chess.WHITE]=0
        assert game.cast_jump(chess.A2, chess.A3) == False
    
    def test_jump_fails_on_opponent_piece(self):
        game = SpellChessGame()
        assert game.cast_jump(chess.F2, chess.F7) == False
    
    def test_jump_fail_if_target_occupied(self):
        game = SpellChessGame()
        assert game.cast_jump(chess.B1, chess.C2) == False
        # Bug: I caught a bug here where we don't block jumps to actual occupied squres
    
    
    def test_jump_cannot_jump_king(self):
        game = SpellChessGame()
        assert game.cast_jump(chess.E1, chess.E3) == False
        # Bug: I caught a bug where the code allows us to jump the king even though based on the spec we cannot do that
         
    
    def test_chebyshev_distance_of_2(self):
        game = SpellChessGame()
        assert chess.E5 not in squares_in_jump_range(chess.E2) 
        assert chess.C5 not in squares_in_jump_range(chess.E2) 
        # Bug: I caught another bug in the code we allow it to go past the chebyshev distance by an offset of 3 and not 2
    
class TestJumpEffect:
    def test_jump_ignores_inbetween_pieces(self):
        game = SpellChessGame()
        game.board.set_piece_at(chess.E3, chess.Piece(chess.PAWN, chess.WHITE))
        assert game.cast_jump(chess.E2, chess.E4)
    
    
    def test_jump_lands_on_empty_square(self):
        game = SpellChessGame()
        assert game.cast_jump(chess.E2, chess.E4)
        assert game.board.piece_at(chess.E4) == chess.Piece(chess.PAWN, chess.WHITE)
    
class TestJumpCoolDown:
    def test_jump_cooldown_prevents_jump(self):
        game = SpellChessGame()
        game.jump_cooldown[chess.WHITE] = 1
        assert game.cast_jump(chess.E2, chess.E4) == False
    
    
    def test_jump_cooldown_decreases_every_turn(self):
        game = SpellChessGame()
        game.jump_cooldown[chess.WHITE] = 2
        game.board.turn = chess.BLACK        
        assert game.jump_cooldown[chess.WHITE] == 1
        # Bug: I caught a bug here where we are not decrementing the cooldown after each new turn
    
    
    def test_jump_caster_cannot_cast_until_cooldown_reaches_zero(self):
        game = SpellChessGame()
        game.jump_cooldown[chess.WHITE] = 2
        assert game.cast_jump(chess.E2, chess.E4) == False
        game.jump_cooldown[chess.WHITE] = 0
        assert game.cast_jump(chess.E2, chess.E4) == True  