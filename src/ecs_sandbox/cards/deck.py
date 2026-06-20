import numpy as np


def new_deck() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    suits = np.repeat(np.arange(4, dtype=np.uint8), 13)
    ranks = np.repeat(np.arange(13, dtype=np.uint8), 4)
    locations = np.zeros(52, dtype=np.uint8)
    return suits, ranks, locations


def sort(ranks: np.ndarray, suits: np.ndarray) -> np.ndarray:
    return np.lexsort((ranks, suits))


def shuffle(seed: int = 42) -> np.ndarray:
    return np.random.default_rng(seed).permutation(52)


def player_hand(locations: np.ndarray, player: int) -> np.ndarray:
    return np.where(locations == player)[0]


def deal(order: np.ndarray, locations: np.ndarray, player: int, n_cards: int) -> None:
    locations[order[range(n_cards)]] = player


def row(
    suits: np.ndarray, ranks: np.ndarray, locations: np.ndarray, i: int
) -> tuple[int, int, int]:
    return (int(suits[i]), int(ranks[i]), int(locations[i]))


SUIT = ["♠", "♥", "♦", "♣"]
RANK = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def card_to_string(suit: int, rank: int) -> str:
    return f"{RANK[rank]}{SUIT[suit]}"
