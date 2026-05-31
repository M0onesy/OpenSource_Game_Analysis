"""Helpers for sanitizing PNG metadata that triggers noisy libpng warnings."""

from __future__ import annotations

from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ICCP_CHUNK = b"iCCP"


def strip_incorrect_iccp_chunk(path: str | Path) -> int:
    """Remove iCCP chunks from a PNG in-place and return the number removed.

    Some tools emit malformed ICC profile metadata that causes:
    ``libpng warning: iCCP: known incorrect sRGB profile``.
    We do a binary chunk rewrite instead of decoding pixels, so the cleanup
    itself does not rely on libpng/Pillow and won't re-trigger the warning.
    """
    path = Path(path)
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"Not a PNG file: {path}")

    pos = len(PNG_SIGNATURE)
    chunks: list[bytes] = []
    removed = 0

    while pos + 8 <= len(data):
        length = int.from_bytes(data[pos:pos + 4], "big")
        chunk_end = pos + 12 + length
        if chunk_end > len(data):
            raise ValueError(f"Corrupt PNG chunk layout: {path}")

        chunk_type = data[pos + 4:pos + 8]
        chunk = data[pos:chunk_end]
        if chunk_type == ICCP_CHUNK:
            removed += 1
        else:
            chunks.append(chunk)

        pos = chunk_end
        if chunk_type == b"IEND":
            break

    if removed:
        path.write_bytes(PNG_SIGNATURE + b"".join(chunks))
    return removed
