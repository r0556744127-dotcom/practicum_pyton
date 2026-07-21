def expected_score(elo_a: int, elo_b: int) -> float:
    """Probability that A beats B (0..1)."""
    return 1.0 / (1.0 + 10 ** ((elo_b - elo_a) / 400.0))
    
def update_pair(elo_winner: int, elo_loser: int, k: int = 32) -> tuple[int, int]:
    """Return (new_winner_elo, new_loser_elo) after one game."""
    exp_w = expected_score(elo_winner, elo_loser)
    exp_l = expected_score(elo_loser, elo_winner)

    new_w = round(elo_winner + k * (1.0 - exp_w))
    new_l = round(elo_loser + k * (0.0 - exp_l))
    return new_w, new_l


if __name__ == "__main__":
    # Equal ratings: winner should gain ~16, loser lose ~16
    w, l = update_pair(1200, 1200)
    print("1200 vs 1200 ->", w, l)
    assert w == 1216 and l == 1184

    # Strong beats weak: smaller gain for the strong player
    w, l = update_pair(1400, 1000)
    print("1400 beats 1000 ->", w, l)
    assert w < 1416   # gains less than 16
    assert l > 984    # loses less than 16
    print("elo OK")