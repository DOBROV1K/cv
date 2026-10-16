import enum
import random


class Handedness(enum.Enum):
    RIGHT = "правая"
    LEFT = "левая"


class RandomTrial:
    def __init__(self, handedness: Handedness, angles_deg: tuple[float, float, float]) -> None:
        self.handedness = handedness
        self.angles_deg = angles_deg


def random_trial(rng: random.Random | None = None) -> RandomTrial:
    if rng is None:
        rng = random
    handedness = rng.choice([Handedness.RIGHT, Handedness.LEFT])
    angles_deg = (
        rng.uniform(0, 360),
        rng.uniform(0, 360),
        rng.uniform(0, 360),
    )
    return RandomTrial(handedness=handedness, angles_deg=angles_deg)
