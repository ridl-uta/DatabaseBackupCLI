from __future__ import annotations

import gzip
from pathlib import Path
import shutil

from db_backup_utility.exceptions.compression_exception import CompressionException


class CompressionService:
    def compress(self, file_path: str, compression_type: str = "gzip") -> str:
        if compression_type != "gzip":
            raise CompressionException(f"Unsupported compression type: {compression_type}")

        source = Path(file_path).expanduser().resolve()
        if source.suffix == ".gz":
            return str(source)

        destination = source.with_suffix(source.suffix + ".gz")
        with source.open("rb") as src, gzip.open(destination, "wb") as dst:
            shutil.copyfileobj(src, dst)
        return str(destination)

    def decompress(self, file_path: str) -> str:
        source = Path(file_path).expanduser().resolve()
        if source.suffix != ".gz":
            return str(source)

        destination = source.with_suffix("")
        with gzip.open(source, "rb") as src, destination.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        return str(destination)

