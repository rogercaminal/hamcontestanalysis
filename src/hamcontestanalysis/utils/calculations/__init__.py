"""Common util calculations."""

import numpy as np


def custom_floor(x: float, precision: float = 0) -> float:
    """Calculates a customized version of the floor rounding function.

    Args:
        x (float): Number to compute the floor from
        precision (float, optional): Precision of the floor. Defaults
            to 0.

    Returns:
        float: rounded number
    """
    return np.round(precision * np.floor(np.round(x / precision, 2)), 2)
