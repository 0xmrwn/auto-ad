from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Gap:
    """Represents a gap between subtitles"""

    start_time: timedelta
    end_time: timedelta
    duration: timedelta
    previous_subtitle: str
    next_subtitle: str
