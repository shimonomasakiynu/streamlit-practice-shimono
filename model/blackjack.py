from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

SUITS = ("Spades", "Hearts", "Diamonds", "Clubs")
RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
RANK_VALUES = {
    "A": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
}


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def base_value(self) -> int:
        return RANK_VALUES[self.rank]

    def label(self) -> str:
        return f"{self.rank} of {self.suit}"


def hand_value(cards: List[Card]) -> int:
    total = sum(card.base_value for card in cards)
    aces = sum(1 for card in cards if card.rank == "A")
    while aces and total + 10 <= 21:
        total += 10
        aces -= 1
    return total


class BlackjackGame:
    """Stateful single player blackjack implementation."""

    def __init__(self, initial_chips: int = 100, rng: Optional[random.Random] = None) -> None:
        if initial_chips <= 0:
            raise ValueError("initial_chips must be a positive integer")

        self.initial_chips = initial_chips
        self._rng = rng or random.Random()
        self.reset()

    # ------------------------------------------------------------------
    def reset(self) -> None:
        self.chips = self.initial_chips
        self.history: List[Dict] = []
        self._deck: List[Card] = []
        self._player_cards: List[Card] = []
        self._dealer_cards: List[Card] = []
        self.current_bet = 0
        self.state = "BETTING"
        self.round_outcome: Optional[str] = None

    # ------------------------------------------------------------------
    @property
    def player_cards(self) -> List[Card]:
        return list(self._player_cards)

    @property
    def dealer_cards(self) -> List[Card]:
        return list(self._dealer_cards)

    @property
    def dealer_upcard(self) -> Optional[Card]:
        if not self._dealer_cards:
            return None
        return self._dealer_cards[0]

    @property
    def player_total(self) -> int:
        return hand_value(self._player_cards)

    @property
    def dealer_total(self) -> int:
        return hand_value(self._dealer_cards)

    @property
    def is_player_turn(self) -> bool:
        return self.state == "PLAYER_TURN"

    @property
    def is_round_over(self) -> bool:
        return self.state == "ROUND_OVER"

    @property
    def cards_remaining(self) -> int:
        return len(self._deck)

    @property
    def is_bankrupt(self) -> bool:
        return self.chips <= 0

    @property
    def last_record(self) -> Optional[Dict]:
        if not self.history:
            return None
        return self.history[-1]

    # ------------------------------------------------------------------
    def start_round(self, bet: int) -> None:
        if self.state != "BETTING":
            raise RuntimeError("Round already in progress")
        if bet <= 0:
            raise ValueError("Bet must be a positive integer")
        if bet > self.chips:
            raise ValueError("Bet cannot exceed current chips")

        self._ensure_deck()
        self.current_bet = bet
        self.chips -= bet
        self._player_cards = [self._draw_card(), self._draw_card()]
        self._dealer_cards = [self._draw_card(), self._draw_card()]
        self.round_outcome = None
        self.state = "PLAYER_TURN"

        player_total = self.player_total
        dealer_total = self.dealer_total
        if player_total == 21 and dealer_total == 21:
            self._finish_round("push")
        elif player_total == 21:
            self._finish_round("player_blackjack")
        elif dealer_total == 21:
            self._finish_round("dealer_blackjack")

    def hit(self) -> Card:
        if self.state != "PLAYER_TURN":
            raise RuntimeError("Hit is only available during the player turn")

        card = self._draw_card()
        self._player_cards.append(card)
        if self.player_total > 21:
            self._finish_round("player_bust")
        return card

    def stand(self) -> None:
        if self.state != "PLAYER_TURN":
            raise RuntimeError("Stand is only available during the player turn")

        self._dealer_play()
        dealer_total = self.dealer_total
        player_total = self.player_total
        if dealer_total > 21:
            self._finish_round("dealer_bust")
        elif dealer_total > player_total:
            self._finish_round("dealer_win")
        elif dealer_total < player_total:
            self._finish_round("player_win")
        else:
            self._finish_round("push")

    def next_round(self) -> None:
        if self.state != "ROUND_OVER":
            raise RuntimeError("Next round can only start after the current round ends")

        self._player_cards = []
        self._dealer_cards = []
        self.current_bet = 0
        self.round_outcome = None
        self.state = "BETTING"

    def reset_shoe(self) -> None:
        self._deck = []

    # ------------------------------------------------------------------
    def _dealer_play(self) -> None:
        while self.dealer_total < 17:
            self._dealer_cards.append(self._draw_card())

    def _finish_round(self, outcome: str) -> None:
        self.state = "ROUND_OVER"
        self.round_outcome = outcome

        chips_before = self.chips
        payout = 0
        if outcome in {"player_win", "dealer_bust"}:
            payout = self.current_bet * 2
        elif outcome == "player_blackjack":
            payout = self.current_bet * 2
        elif outcome == "push":
            payout = self.current_bet

        self.chips += payout
        delta = self.chips - chips_before

        record: Dict = {
            "outcome": outcome,
            "bet": self.current_bet,
            "delta": delta,
            "player_cards": [card.label() for card in self._player_cards],
            "dealer_cards": [card.label() for card in self._dealer_cards],
            "player_total": self.player_total,
            "dealer_total": self.dealer_total,
            "chips_after": self.chips,
        }
        self.history.append(record)
        self.current_bet = 0

    def _ensure_deck(self) -> None:
        if len(self._deck) < 15:
            self._deck = [Card(rank=rank, suit=suit) for suit in SUITS for rank in RANKS]
            self._rng.shuffle(self._deck)

    def _draw_card(self) -> Card:
        if not self._deck:
            self._ensure_deck()
        return self._deck.pop()


__all__ = ["BlackjackGame", "Card", "hand_value"]
