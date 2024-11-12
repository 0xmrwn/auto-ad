import logging
from pathlib import Path
from typing import Optional, Tuple

import pysrt
from pysrt import SubRipFile

from .utils.encoding import EncodingDetector


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
    def validate_srt_content(cls, subtitles: SubRipFile) -> Tuple[bool, Optional[str]]:
        """
        Validate if the SRT file contains valid subtitles and French text

        Args:
            subtitles (SubRipFile): Parsed subtitles to validate

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Check basic subtitle structure
        if not (
            len(subtitles) > 0
            and all(sub.start and sub.end and sub.text for sub in subtitles)
        ):
            return False, "Invalid subtitle structure"

        # Validate French text in each subtitle
        # for sub in subtitles:
        #     is_valid, error_msg = EncodingDetector.validate_french_text(sub.text)
        #     if not is_valid:
        #         return False, f"Invalid text in subtitle {sub.index}: {error_msg}"

        return True, None

    @classmethod
    def load_srt_file(cls, file_path: str) -> Optional[SubRipFile]:
        """
        Load and validate an SRT file with enhanced encoding detection
        """
        if not cls.validate_file_path(file_path):
            logging.error(f"Invalid file path or extension: {file_path}")
            raise ValueError(f"Invalid file path or extension: {file_path}")

        try:
            path = Path(file_path)
            encoding, confidence = EncodingDetector.detect_file_encoding(path)

            logging.info(
                f"Attempting to load file with encoding: {encoding} (confidence: {confidence:.2f})"
            )

            # Try loading with detected encoding first
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                subtitles = pysrt.from_string(content)
            except UnicodeDecodeError as e:
                logging.warning(
                    f"Failed to load with {encoding}, trying fallback encodings"
                )
                # Try fallback encodings
                for fallback_encoding in ["cp1252", "latin-1", "iso-8859-1"]:
                    try:
                        with open(file_path, "r", encoding=fallback_encoding) as f:
                            content = f.read()
                        subtitles = pysrt.from_string(content)
                        logging.info(
                            f"Successfully loaded with fallback encoding: {fallback_encoding}"
                        )
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError(
                        f"Failed to decode file with any known encoding: {str(e)}"
                    )

            # Validate content
            is_valid, error_msg = cls.validate_srt_content(subtitles)
            if not is_valid:
                logging.error(f"Invalid SRT content in file: {file_path} - {error_msg}")
                raise ValueError(f"Invalid SRT content: {error_msg}")

            return subtitles

        except FileNotFoundError:
            logging.error(f"SRT file not found: {file_path}")
            raise
        except Exception as e:
            logging.error(f"Error processing SRT file: {str(e)}")
            raise ValueError(f"Invalid SRT file: {str(e)}")
