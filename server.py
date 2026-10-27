"""Flask REST API and browser entry point."""

from pathlib import Path
from threading import RLock
from uuid import uuid4

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

from game import HangmanGame, InvalidGuess
from word_manager import DIFFICULTIES, WordManager


def create_app(word_manager: WordManager | None = None) -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    manager = word_manager or WordManager(Path(__file__).parent / "words")
    games: dict[str, HangmanGame] = {}
    lock = RLock()

    def body_with(required_field: str):
        if not request.is_json:
            return None, (jsonify(error="Send a JSON object with Content-Type: application/json."), 415)
        try:
            body = request.get_json()
        except BadRequest:
            return None, (jsonify(error="Malformed JSON."), 400)
        if not isinstance(body, dict) or set(body) != {required_field}:
            return None, (jsonify(error=f"Send only the {required_field} field."), 400)
        return body, None

    def get_game(game_id: str):
        game = games.get(game_id)
        if game is None:
            return None, (jsonify(error="Game not found."), 404)
        return game, None

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.post("/api/games")
    def create_game():
        body, error = body_with("difficulty")
        if error:
            return error
        difficulty = body["difficulty"]
        if not isinstance(difficulty, str) or difficulty not in DIFFICULTIES:
            return jsonify(error="Difficulty must be easy, medium, or hard."), 400
        game = HangmanGame(manager.choose(difficulty), difficulty)
        game_id = uuid4().hex
        with lock:
            games[game_id] = game
        return jsonify(game_id=game_id, **game.public_state()), 201

    @app.get("/api/games/<game_id>")
    def game_state(game_id: str):
        with lock:
            game, error = get_game(game_id)
            if error:
                return error
            return jsonify(game_id=game_id, **game.public_state())

    @app.post("/api/games/<game_id>/guess")
    def guess(game_id: str):
        body, error = body_with("letter")
        if error:
            return error
        with lock:
            game, error = get_game(game_id)
            if error:
                return error
            try:
                correct = game.guess(body["letter"])
            except InvalidGuess as exc:
                letter = body["letter"]
                conflict = game.status != "playing" or (
                    isinstance(letter, str) and letter.lower() in game.guessed_letters
                )
                return jsonify(error=str(exc), game_id=game_id, **game.public_state()), 409 if conflict else 400
            return jsonify(game_id=game_id, correct=correct, **game.public_state())

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify(error="Endpoint not found."), 404
        return "Not found", 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False)
