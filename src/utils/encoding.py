from pathlib import Path
from typing import Optional, Tuple

import chardet


class EncodingDetector:
    """Handles text encoding detection and validation"""

    PREFERRED_ENCODINGS = ["utf-8", "utf-8-sig", "iso-8859-1", "cp1252"]

    @classmethod
    def detect_file_encoding(cls, file_path: Path) -> Tuple[str, float]:
        """
        Detect the encoding of a file using chardet and fallback methods
        """
        raw_bytes = file_path.read_bytes()

        # First try to decode with UTF-8-SIG (BOM)
        try:
            raw_bytes.decode("utf-8-sig")
            return "utf-8-sig", 1.0
        except UnicodeDecodeError:
            pass

        # Try chardet detection
        detection = chardet.detect(raw_bytes)
        detected_encoding = detection["encoding"]
        confidence = detection["confidence"]

        # If confidence is low or encoding is None, try our preferred encodings
        if not detected_encoding or confidence < 0.8:
            for enc in cls.PREFERRED_ENCODINGS:
                try:
                    raw_bytes.decode(enc)
                    return enc, 1.0
                except UnicodeDecodeError:
                    continue

        # If all else fails, default to Windows-1252 (common for French files)
        if not detected_encoding:
            return "cp1252", 0.5

        return detected_encoding.lower(), confidence

    @classmethod
    def validate_french_text(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if text contains valid French characters

        Args:
            text: Text to validate

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Common French characters and punctuation
        french_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "éèêëàâäôöûüùïîçÉÈÊËÀÂÄÔÖÛÜÙÏÎÇ"
            "0123456789"
            ' .,!?-:;«»""\'()'
        )

        invalid_chars = set()
        for char in text:
            if char not in french_chars and char not in {"\n", "\r"}:
                invalid_chars.add(char)

        if invalid_chars:
            return False, f"Invalid characters found: {sorted(invalid_chars)}"

        return True, None
