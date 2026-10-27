import pytest

from word_manager import WordManager


def test_all_difficulties_and_duplicates(tmp_path):
    for difficulty in ("easy", "medium", "hard"):
        (tmp_path / f"{difficulty}.txt").write_text("Apple\napple\nberry\n", encoding="utf-8")
    manager = WordManager(tmp_path)
    for difficulty in ("easy", "medium", "hard"):
        assert manager.choose(difficulty) in {"apple", "berry"}
        assert len(manager.words[difficulty]) == 2
    with pytest.raises(ValueError):
        manager.choose("expert")


def test_invalid_word_rejected(tmp_path):
    for difficulty in ("easy", "medium", "hard"):
        (tmp_path / f"{difficulty}.txt").write_text("a-b\n", encoding="utf-8")
    with pytest.raises(ValueError):
        WordManager(tmp_path)
