import pytest

from game import HangmanGame, InvalidGuess


def test_correct_guess_reveals_all_occurrences_and_win():
    game = HangmanGame("apple", "easy")
    assert game.public_state()["pattern"] == "_ _ _ _ _"
    assert "word" not in game.public_state()
    for letter in "aple":
        assert game.guess(letter)
    assert game.status == "won"
    assert game.pattern == "a p p l e"
    assert game.public_state()["word"] == "apple"
    with pytest.raises(InvalidGuess):
        game.guess("z")


def test_misses_loss_and_no_more_guesses():
    game = HangmanGame("cat", "easy")
    for letter in "bdefgh":
        assert not game.guess(letter)
    assert game.remaining_guesses == 0
    assert game.status == "lost"
    assert game.public_state()["word"] == "cat"
    with pytest.raises(InvalidGuess):
        game.guess("c")


@pytest.mark.parametrize("letter", ["", "ab", "5", "é", None, 3, ["a"]])
def test_invalid_guesses_do_not_change_state(letter):
    game = HangmanGame("cat", "easy")
    with pytest.raises(InvalidGuess):
        game.guess(letter)
    assert game.guessed_letters == []


def test_duplicate_is_rejected_without_penalty():
    game = HangmanGame("cat", "easy")
    game.guess("B")
    with pytest.raises(InvalidGuess):
        game.guess("b")
    assert game.remaining_guesses == 5
