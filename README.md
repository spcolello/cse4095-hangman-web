# Hangman web game

A Flask-backed Hangman game for the CSE 4095 web application assignment. The Python game engine owns the answer and rules; the browser uses `fetch()` to create games and submit guesses. No terminal client, bots, evaluation system, or leaderboard are included because the assignment excludes them.

**Live app:** <https://cse4095-hangman-web.onrender.com/>  
**GitHub repository:** <https://github.com/spcolello/cse4095-hangman-web>

## Run locally

Use Python 3.10 or newer. From this directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python server.py
```

Open <http://127.0.0.1:5000/>. Choose a difficulty, press **New game**, and guess with the letter buttons or a physical keyboard. Press **New game** at any time to start over. On macOS/Linux, activate with `source .venv/bin/activate`.

Run tests with `python -m pytest -q`.

## API

All request bodies are JSON objects with exactly the documented field. Errors return JSON with an `error` message. The three required endpoints are:

| Method | Path | Request | Success |
| --- | --- | --- | --- |
| POST | `/api/games` | `{"difficulty":"easy"}` | 201, new game state and `game_id` |
| GET | `/api/games/{game_id}` | none | 200, current game state |
| POST | `/api/games/{game_id}/guess` | `{"letter":"a"}` | 200, updated state and `correct` |

`difficulty` accepts `easy`, `medium`, or `hard`. Guesses accept one ASCII letter, case insensitive. The game allows six incorrect letters. Repeated guesses and guesses after a game ends return 409; malformed fields return 400; an unknown game ID returns 404; a non-JSON request returns 415.

While a game is `playing`, the response contains `pattern`, `guessed_letters`, `incorrect_letters`, `remaining_guesses`, `max_incorrect_guesses`, `difficulty`, and `status`, but **never** `word`. The `word` field appears only on `won` or `lost`.

Example using curl:

```bash
curl -X POST http://127.0.0.1:5000/api/games -H "Content-Type: application/json" -d '{"difficulty":"easy"}'
curl -X POST http://127.0.0.1:5000/api/games/GAME_ID/guess -H "Content-Type: application/json" -d '{"letter":"e"}'
curl http://127.0.0.1:5000/api/games/GAME_ID
```

## Project structure

- `game.py`: independent game rules and client-safe state serialization.
- `word_manager.py` and `words/`: validated word lists and random selection.
- `server.py`: Flask routes and per-game in-memory state.
- `static/`: browser markup, styles, and API-driven client.
- `tests/`: engine, word, and API tests.
- `render.yaml`: Render deployment blueprint.
- `SPECIFICATION.md`: unmodified original reference specification; its bot and leaderboard sections are outside this assignment.
- `TODO.md`: reduced, phased assignment plan and verified status.

## Deploy on Render

The current service was deployed from the linked GitHub repository as a Render Python 3 web service on the Free plan. It uses build command `pip install -r requirements.txt` and start command `gunicorn --bind 0.0.0.0:$PORT --workers 1 server:app`. The included `render.yaml` also supports a Blueprint setup. Render reported the first deployment live on October 27, 2026. The HTTPS browser game and the three API endpoints were then tested. Keep the service available through grading.

The service stores games in memory and uses one Gunicorn worker so requests for a game reach the same process. A Render restart clears active games. This is acceptable for the assignment's casual game, but persistent games would require a shared data store.

## How a guess moves through the application

The user clicks a letter (or presses a key). `static/app.js` sends a JSON `POST` to `/api/games/{game_id}/guess`. Flask validates the request, looks up the game, and calls `HangmanGame.guess()`. The engine changes the guessed-letter list and remaining lives, then returns a public state object. JavaScript renders the pattern, keyboard, remaining count, drawing, and result from that response. The browser never calculates whether a guess is correct from the hidden answer.

## Manual browser check

Open browser Developer Tools, select **Network**, then press a letter. Select the request ending in `/guess` and inspect its JSON request and response. While the game is active, the response must not have a `word` field. Continue until a win or loss, then start another game without refreshing the page.
