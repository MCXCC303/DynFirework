"""ColorBlock 时间线常量 (tick-based)."""
import math
from ...timeline.theme import *

PIXELS_PER_TICK_DEFAULT = 3.0

def _nice_interval(min_interval: float) -> float:
	"""向上取整到易于阅读的数值: 1, 2, 5, 10, 20, 50, ..."""
	if min_interval <= 0:
		return 1.0
	magnitude = 10 ** math.floor(math.log10(min_interval))
	residual = min_interval / magnitude
	if residual <= 1:
		nice = 1
	elif residual <= 2:
		nice = 2
	elif residual <= 5:
		nice = 5
	else:
		nice = 10
	return nice * magnitude
