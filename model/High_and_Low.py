from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class RecordedRound:
    """Round definition captured in the sample data."""

    round: int
    base_card: int
    result_card: int
    remaining_deck: List[int]

    @classmethod
    def from_payload(cls, payload: Dict) -> "RecordedRound":
        return cls(
            round=payload["round"],
            base_card=payload["base_card"],
            result_card=payload["result_card"],
            remaining_deck=payload.get("remaining_deck", []),
        )


class HighLowGame:
    """High and Low game that replays rounds defined in sample data."""

    def __init__(self, initial_chips: int, rounds: List[RecordedRound], deck: List[int]):
        if not rounds:
            raise ValueError("At least one round definition is required")

        self.initial_chips = initial_chips
        self._rounds = rounds
        self._initial_deck = list(deck)
        if not self._initial_deck:
            raise ValueError("Deck must contain at least one card")

        self.reset()

    # ------------------------------------------------------------------
    # Public properties
    @property
    def total_rounds(self) -> int:
        return len(self._rounds)

    @property
    def round_number(self) -> int:
        return self._current_index + 1

    @property
    def is_finished(self) -> bool:
        return self._current_index >= len(self._rounds)

    @property
    def current_round(self) -> Optional[RecordedRound]:
        if self.is_finished:
            return None
        return self._rounds[self._current_index]

    @property
    def deck(self) -> List[int]:
        return list(self._deck)

    @property
    def history(self) -> List[Dict]:
        return list(self._history)

    # ------------------------------------------------------------------
    def expose_base_card(self) -> int:
        round_def = self.current_round
        if round_def is None:
            raise RuntimeError("No round is available")

        if not self._base_drawn:
            self._remove_card(round_def.base_card)
            self._base_drawn = True

        return round_def.base_card

    def play_round(self, player_choice: str, bet: int) -> Dict:
        if self.is_finished:
            raise RuntimeError("All rounds have already been played")

        if bet <= 0:
            raise ValueError("Bet must be a positive integer")

        if bet > self.chips:
            raise ValueError("Bet cannot exceed the current number of chips")

        round_def = self.current_round
        assert round_def is not None

        base_card = self.expose_base_card()
        result_card = round_def.result_card

        normalized_choice = player_choice.capitalize()
        if normalized_choice not in {"High", "Low"}:
            raise ValueError("player_choice must be either 'High' or 'Low'")

        if result_card == base_card:
            outcome = "draw"
            delta = 0
        else:
            correct_choice = "High" if result_card > base_card else "Low"
            if normalized_choice == correct_choice:
                outcome = "win"
                delta = bet
            else:
                outcome = "lose"
                delta = -bet

        chips_before = self.chips
        self.chips += delta
        self._remove_card(result_card)

        result = {
            "round": round_def.round,
            "base_card": base_card,
            "result_card": result_card,
            "player_choice": normalized_choice,
            "bet": bet,
            "outcome": outcome,
            "delta": delta,
            "chips_before": chips_before,
            "chips_after": self.chips,
            "remaining_deck": self.deck,
        }

        self._history.append(result)
        self._current_index += 1
        self._base_drawn = False
        return result

    def reset(self) -> None:
        self.chips = self.initial_chips
        self._deck = list(self._initial_deck)
        self._current_index = 0
        self._history: List[Dict] = []
        self._base_drawn = False

    # ------------------------------------------------------------------
    def _remove_card(self, card: int) -> None:
        try:
            self._deck.remove(card)
        except ValueError as exc:
            raise ValueError(f"Card {card} is not available in the deck") from exc

    # ------------------------------------------------------------------
    @classmethod
    def from_file(cls, path: Path | str) -> "HighLowGame":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))

        initial_chips = payload.get("initial_chips")
        if initial_chips is None:
            raise ValueError("'initial_chips' not found in sample data")

        deck = payload.get("deck")
        if not isinstance(deck, list):
            raise ValueError("'deck' must be a list in sample data")

        rounds_payload = payload.get("rounds")
        if not isinstance(rounds_payload, list):
            raise ValueError("'rounds' must be a list in sample data")

        rounds = [RecordedRound.from_payload(item) for item in rounds_payload]
        return cls(initial_chips=initial_chips, rounds=rounds, deck=deck)


def load_sample_game(sample_name: str = "highlow_round3.json") -> HighLowGame:
    sample_path = Path(__file__).resolve().parent.parent / "sample_data" / sample_name
    if not sample_path.exists():
        raise FileNotFoundError(f"Sample data '{sample_name}' not found at {sample_path}")

    return HighLowGame.from_file(sample_path)
