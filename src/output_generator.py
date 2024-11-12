from datetime import timedelta
from pathlib import Path
from typing import List

from pysrt import SubRipFile, SubRipItem, SubRipTime

from .models import Gap


class OutputGenerator:
    """Handles the generation of output files and summaries for detected gaps"""

    def __init__(self, gap_text: str = "[Silence]"):
        """
        Initialize the output generator

        Args:
            gap_text (str): Text to use for gap entries in the SRT file
        """
        self.gap_text = gap_text

    @staticmethod
    def _timedelta_to_srt_time(td: timedelta) -> SubRipTime:
        """Convert a timedelta object to SubRipTime"""
        total_seconds = td.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds * 1000) % 1000)

        return SubRipTime(
            hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds
        )

    def generate_gap_srt(self, gaps: List[Gap], output_path: Path) -> None:
        """
        Generate a new SRT file containing the detected gaps

        Args:
            gaps (List[Gap]): List of detected gaps
            output_path (Path): Path where to save the output SRT file
        """
        srt_file = SubRipFile()

        for index, gap in enumerate(gaps, start=1):
            # Create a new subtitle entry for the gap
            item = SubRipItem(
                index=index,
                start=self._timedelta_to_srt_time(gap.start_time),
                end=self._timedelta_to_srt_time(gap.end_time),
                text=self.gap_text,
            )
            srt_file.append(item)

        # Save with UTF-8 encoding and BOM for better Windows compatibility
        srt_file.save(output_path, encoding="utf-8-sig")

    def generate_summary(
        self, gaps: List[Gap], stats: dict, include_details: bool = True
    ) -> str:
        """
        Generate a text summary of the detected gaps

        Args:
            gaps (List[Gap]): List of detected gaps
            stats (dict): Statistics dictionary from GapDetector
            include_details (bool): Whether to include detailed gap information

        Returns:
            str: Formatted summary text
        """
        summary = [
            "Gap Detection Summary",
            "===================",
            f"Total Gaps Found: {stats['total_gaps']}",
            f"Total Gap Duration: {self._format_timedelta(stats['total_duration'])}",
            f"Average Gap Duration: {self._format_timedelta(stats['average_duration'])}",
            f"Minimum Gap Duration: {self._format_timedelta(stats['min_duration'])}",
            f"Maximum Gap Duration: {self._format_timedelta(stats['max_duration'])}",
            "",
        ]

        if include_details and gaps:
            summary.extend(["Detailed Gap Information", "======================"])

            for i, gap in enumerate(gaps, start=1):
                summary.extend(
                    [
                        f"\nGap #{i}:",
                        f"Start Time: {self._format_timedelta(gap.start_time)}",
                        f"End Time: {self._format_timedelta(gap.end_time)}",
                        f"Duration: {self._format_timedelta(gap.duration)}",
                        "Context:",
                        f"  Previous subtitle: {gap.previous_subtitle}",
                        f"  Next subtitle: {gap.next_subtitle}",
                        "-" * 40,
                    ]
                )

        return "\n".join(summary)

    def save_summary(self, summary: str, output_path: Path) -> None:
        """
        Save the summary to a file

        Args:
            summary (str): Generated summary text
            output_path (Path): Path where to save the summary
        """
        output_path.write_text(summary, encoding="utf-8")

    @staticmethod
    def _format_timedelta(td: timedelta) -> str:
        """
        Format a timedelta object into a readable string

        Args:
            td (timedelta): Time delta to format

        Returns:
            str: Formatted time string (HH:MM:SS.mmm)
        """
        total_seconds = td.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds * 1000) % 1000)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
