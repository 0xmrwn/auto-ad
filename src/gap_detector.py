from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pysrt

from src.input_handler import InputHandler
from src.models import Gap


class GapDetector:
    """Detects gaps between subtitles in SRT files"""

    def __init__(self, min_gap_duration: float = 1.0):
        """
        Initialize the gap detector

        Args:
            min_gap_duration (float): Minimum gap duration in seconds to detect
        """
        self.min_gap_duration = timedelta(seconds=min_gap_duration)

    def detect_gaps(self, srt_path: Path) -> Tuple[List[Gap], Dict]:
        """
        Detect gaps in a subtitle file

        Args:
            srt_path (Path): Path to the SRT file

        Returns:
            Tuple[List[Gap], Dict]: List of detected gaps and statistics dictionary
        """
        # Load the SRT file using InputHandler
        subtitles = InputHandler.load_srt_file(str(srt_path))

        # Sort subtitles by start time
        sorted_subs = sorted(subtitles, key=lambda x: x.start.ordinal)

        gaps = []
        total_duration = timedelta()

        # Iterate through subtitles to find gaps
        for i in range(len(sorted_subs) - 1):
            current_sub = sorted_subs[i]
            next_sub = sorted_subs[i + 1]

            # Calculate gap between current subtitle end and next subtitle start
            gap_start = current_sub.end
            gap_end = next_sub.start
            gap_duration = timedelta(milliseconds=(gap_end.ordinal - gap_start.ordinal))

            # If gap is larger than minimum duration, record it
            if gap_duration >= self.min_gap_duration:
                gap = Gap(
                    start_time=timedelta(milliseconds=gap_start.ordinal),
                    end_time=timedelta(milliseconds=gap_end.ordinal),
                    duration=gap_duration,
                    previous_subtitle=current_sub.text,
                    next_subtitle=next_sub.text,
                )
                gaps.append(gap)
                total_duration += gap_duration

        # Calculate statistics
        stats = self._calculate_stats(gaps, total_duration)

        return gaps, stats

    def _calculate_stats(self, gaps: List[Gap], total_duration: timedelta) -> Dict:
        """
        Calculate statistics for the detected gaps

        Args:
            gaps (List[Gap]): List of detected gaps
            total_duration (timedelta): Total duration of all gaps

        Returns:
            Dict: Dictionary containing gap statistics
        """
        if not gaps:
            return {
                "total_gaps": 0,
                "total_duration": timedelta(),
                "average_duration": timedelta(),
                "min_duration": timedelta(),
                "max_duration": timedelta(),
            }

        return {
            "total_gaps": len(gaps),
            "total_duration": total_duration,
            "average_duration": total_duration / len(gaps),
            "min_duration": min(gap.duration for gap in gaps),
            "max_duration": max(gap.duration for gap in gaps),
        }
