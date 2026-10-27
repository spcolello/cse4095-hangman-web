# Assignment TODO - reduced Hangman scope

This plan adapts the provided `TODO.md` to the web game required by the assignment. The original specification is retained in `SPECIFICATION.md`; its terminal client, bots, evaluation, scoring, leaderboard, and replay work are out of scope.

## Phase 1 - Game engine and word management

- [x] Keep `HangmanGame` independent of Flask and the browser.
- [x] Validate letters, reject duplicates, track misses, and prevent guesses after a win/loss.
- [x] Return a masked pattern and reveal the answer only after a game ends.
- [x] Load and validate Easy, Medium, and Hard lists; select words randomly.
- [x] Test rules, word selection, errors, wins, and losses.

## Phase 2 - Flask server and REST API

- [x] Implement `POST /api/games`, `GET /api/games/{game_id}`, and `POST /api/games/{game_id}/guess`.
- [x] Use unique IDs and separate in-memory game states.
- [x] Validate JSON and return suitable 201, 200, 400, 404, 409, and 415 statuses.
- [x] Keep the answer out of active-game API responses.
- [x] Test normal and invalid requests.

## Phase 3 - Browser client

- [x] Build responsive HTML/CSS/JavaScript interface with difficulty selection and new-game flow.
- [x] Support clicking letters and physical keyboard input.
- [x] Render masked word, guessed letters, remaining misses, six-part SVG figure, and win/loss messages.
- [x] Use `fetch()` for all game actions and handle request errors.
- [x] Verify a browser guess, complete loss, and new game without reloading.

## Phase 4 - Final test and documentation

- [x] Run engine and API automated tests (`25 passed`).
- [x] Play a complete game in the local browser and verify restart.
- [x] Write local setup, API, architecture, and deployment instructions in `README.md`.
- [ ] Inspect a guess request and JSON response in **Chrome Developer Tools** for the demonstration.

## Phase 5 - Deployment and submission

- [x] Provide `requirements.txt`, `render.yaml`, and `.gitignore`.
- [ ] Create and push the GitHub repository.
- [ ] Deploy to Render and verify an HTTPS browser game and API.
- [ ] Submit the repository URL and deployed URL through HuskyCT.
- [ ] Record the 2-3 minute deployed-app demonstration and submit it.
- [ ] Submit the final 1-2 page PDF report.

## Out of scope

- Terminal client
- Automated bots or bot evaluation
- Scoring and leaderboard
- Logging and replay
