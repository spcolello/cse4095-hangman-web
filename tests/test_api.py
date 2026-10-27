import pytest

from server import create_app


class FixedWords:
    def choose(self, difficulty):
        return {"easy": "cat", "medium": "planet", "hard": "algorithm"}[difficulty]


@pytest.fixture
def client():
    return create_app(FixedWords()).test_client()


def create(client, difficulty="easy"):
    response = client.post("/api/games", json={"difficulty": difficulty})
    assert response.status_code == 201
    return response.json


def test_start_all_difficulties_and_separate_games(client):
    ids = set()
    for difficulty, size in (("easy", 3), ("medium", 6), ("hard", 9)):
        state = create(client, difficulty)
        ids.add(state["game_id"])
        assert len(state["pattern"].split()) == size
        assert state["remaining_guesses"] == 6
        assert "word" not in state
    assert len(ids) == 3


def test_correct_wrong_duplicate_and_hidden_word(client):
    first = create(client)
    second = create(client)
    game_id = first["game_id"]
    response = client.post(f"/api/games/{game_id}/guess", json={"letter": "a"})
    assert response.status_code == 200
    assert response.json["correct"] is True
    assert response.json["pattern"] == "_ a _"
    assert "word" not in response.json
    response = client.post(f"/api/games/{game_id}/guess", json={"letter": "z"})
    assert response.json["remaining_guesses"] == 5
    assert response.json["incorrect_letters"] == ["z"]
    response = client.post(f"/api/games/{game_id}/guess", json={"letter": "z"})
    assert response.status_code == 409
    assert response.json["remaining_guesses"] == 5
    assert client.get(f"/api/games/{second['game_id']}").json["guessed_letters"] == []


def test_win_loss_and_new_game(client):
    won_id = create(client)["game_id"]
    for letter in "cat":
        response = client.post(f"/api/games/{won_id}/guess", json={"letter": letter})
    assert response.json["status"] == "won"
    assert response.json["word"] == "cat"
    assert client.post(f"/api/games/{won_id}/guess", json={"letter": "z"}).status_code == 409
    lost_id = create(client)["game_id"]
    for letter in "bdefgh":
        response = client.post(f"/api/games/{lost_id}/guess", json={"letter": letter})
    assert response.json["status"] == "lost"
    assert response.json["word"] == "cat"
    assert create(client)["status"] == "playing"


@pytest.mark.parametrize("body,status", [({"difficulty": "expert"}, 400), ({}, 400), ({"difficulty": 3}, 400), ({"difficulty": "easy", "word": "cat"}, 400)])
def test_invalid_create(client, body, status):
    assert client.post("/api/games", json=body).status_code == status


@pytest.mark.parametrize("letter,status", [("", 400), ("ab", 400), (7, 400), (["a"], 400), ("é", 400)])
def test_invalid_letter(client, letter, status):
    game_id = create(client)["game_id"]
    assert client.post(f"/api/games/{game_id}/guess", json={"letter": letter}).status_code == status
    assert client.get(f"/api/games/{game_id}").json["guessed_letters"] == []


def test_bad_requests_and_page(client):
    game_id = create(client)["game_id"]
    assert client.get("/").status_code == 200
    assert b"/static/app.js" in client.get("/").data
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/api/games/missing").status_code == 404
    assert client.post("/api/games", data="not json", content_type="application/json").status_code == 400
    assert client.post("/api/games", data="hello", content_type="text/plain").status_code == 415
    assert client.post(f"/api/games/{game_id}/guess", json={"letter": "a", "word": "cat"}).status_code == 400
    assert client.get("/api/unknown").status_code == 404
