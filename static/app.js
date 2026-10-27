"use strict";

const difficulty = document.querySelector("#difficulty");
const newGameButton = document.querySelector("#new-game");
const message = document.querySelector("#message");
const pattern = document.querySelector("#pattern");
const guessed = document.querySelector("#guessed");
const remaining = document.querySelector("#remaining");
const keyboard = document.querySelector("#keyboard");
const parts = [...document.querySelectorAll("[data-part]")];

let gameId = null;
let state = null;
let busy = false;

async function api(path, options = {}) {
  const response = await fetch(path, options);
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("The server returned an unreadable response.");
  }
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status}).`);
  return data;
}

function render() {
  const active = state?.status === "playing";
  pattern.replaceChildren();
  if (state) {
    for (const slot of state.pattern.split(" ")) {
      const element = document.createElement("span");
      element.className = "slot";
      element.textContent = slot === "_" ? "" : slot;
      pattern.append(element);
    }
    pattern.setAttribute("aria-label", `Word pattern: ${state.pattern.split(" ").map(c => c === "_" ? "blank" : c).join(", ")}`);
    guessed.textContent = state.guessed_letters.length ? state.guessed_letters.map(c => c.toUpperCase()).join(", ") : "None yet";
    remaining.textContent = state.remaining_guesses;
    const misses = state.max_incorrect_guesses - state.remaining_guesses;
    parts.forEach((part, index) => part.classList.toggle("visible", index < misses));
    if (state.status === "won") setMessage(`You won! The word was ${state.word.toUpperCase()}.`);
    if (state.status === "lost") setMessage(`Game over. The word was ${state.word.toUpperCase()}.`);
  }
  for (const button of keyboard.querySelectorAll("button")) {
    const letter = button.dataset.letter;
    const used = state?.guessed_letters.includes(letter);
    button.disabled = !active || busy || used;
    button.classList.toggle("correct", Boolean(used && !state.incorrect_letters.includes(letter)));
    button.classList.toggle("incorrect", Boolean(used && state.incorrect_letters.includes(letter)));
  }
  newGameButton.disabled = busy;
  difficulty.disabled = busy;
}

function setMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle("error", isError);
}

async function startGame() {
  if (busy) return;
  busy = true;
  render();
  setMessage("Starting a new game...");
  try {
    const next = await api("/api/games", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ difficulty: difficulty.value })
    });
    state = next;
    gameId = next.game_id;
    setMessage("Guess a letter to begin.");
  } catch (error) {
    setMessage(error.message, true);
  } finally {
    busy = false;
    render();
  }
}

async function guessLetter(letter) {
  if (busy || state?.status !== "playing" || state.guessed_letters.includes(letter)) return;
  busy = true;
  render();
  try {
    const next = await api(`/api/games/${encodeURIComponent(gameId)}/guess`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ letter })
    });
    state = next;
    if (next.status === "playing") setMessage(next.correct ? "Good guess. Keep going." : "That letter is not in the word.");
  } catch (error) {
    setMessage(error.message, true);
  } finally {
    busy = false;
    render();
  }
}

for (const letter of "abcdefghijklmnopqrstuvwxyz") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "letter";
  button.dataset.letter = letter;
  button.textContent = letter.toUpperCase();
  button.setAttribute("aria-label", `Guess ${letter.toUpperCase()}`);
  button.addEventListener("click", () => guessLetter(letter));
  keyboard.append(button);
}

newGameButton.addEventListener("click", startGame);
document.addEventListener("keydown", event => {
  if (event.altKey || event.ctrlKey || event.metaKey || event.target === difficulty) return;
  if (/^[a-z]$/i.test(event.key)) guessLetter(event.key.toLowerCase());
});
render();
