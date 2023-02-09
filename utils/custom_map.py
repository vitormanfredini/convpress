"""
functions to map values from one domain to another.
"""
import math

def map_easein(percentage: float) -> float:
    """
    Receive a value between 0 and 1
    and also returns a value between 0 and 1
    but mapped to a growing curve.
    Values closer to zero get valuyes closer to zero
    and ramp up fast when it's closer to 1.
    """
    return math.cos(math.radians(-90 + percentage * 90))
