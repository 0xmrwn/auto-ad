import logging
from pathlib import Path
from typing import Optional

import pysrt
from pysrt import SubRipFile


class InputHandler:
    """Handles SRT file input validation and loading"""

    VALID_EXTENSIONS = {".srt"}

    @classmethod
    def validate_file_path(cls, file_path: str) -> bool:
        """
        Validate if the given path exists and has a valid extension

        Args:
            file_path (str): Path to the file to validate

        Returns:
            bool: True if path is valid, False otherwise
        """
        path = Path(file_path)
        return path.exists() and path.suffix.lower() in cls.VALID_EXTENSIONS

    @classmethod
    def validate_srt_content(cls, subtitles: SubRipFile) -> bool:
        """
        Validate if the SRT file contains valid subtitles

        Args:
            subtitles (SubRipFile): Parsed subtitles to validate

        Returns:
            bool: True if content is valid, False otherwise
        """
        return len(subtitles) > 0 and all(
            sub.start and sub.end and sub.text for sub in subtitles
        )

    @classmethod
    def load_srt_file(cls, file_path: str) -> Optional[SubRipFile]:
        """
        Load and validate an SRT file

        Args:
            file_path (str): Path to the SRT file

        Returns:
            Optional[SubRipFile]: Parsed subtitles if valid, None otherwise

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid or has wrong format
        """
        if not cls.validate_file_path(file_path):
            logging.error(f"Invalid file path or extension: {file_path}")
            raise ValueError(f"Invalid file path or extension: {file_path}")

        try:
            subtitles = pysrt.open(file_path)

            if not cls.validate_srt_content(subtitles):
                logging.error(f"Invalid SRT content in file: {file_path}")
                raise ValueError(f"Invalid SRT content in file: {file_path}")

            return subtitles

        except FileNotFoundError:
            logging.error(f"SRT file not found: {file_path}")
            raise
        except Exception as e:
            logging.error(f"Error processing SRT file: {str(e)}")
            raise ValueError(f"Invalid SRT file: {str(e)}")
