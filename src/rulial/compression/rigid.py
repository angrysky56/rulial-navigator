import lzma
import gzip
import zlib

def compress_ratio_lzma(data: bytes) -> float:
    """
    Returns compression ratio using LZMA (good for finding long-range redundancy).
    Ratio = Compressed Size / Original Size
    Lower is more compressible (Ordered). Higher is less compressible (Chaotic).
    """
    if not data:
        return 0.0
    compressed = lzma.compress(data)
    return len(compressed) / len(data)

def compress_ratio_gzip(data: bytes) -> float:
    """
    Returns compression ratio using GZIP (faster, good for local redundancy).
    """
    if not data:
        return 0.0
    compressed = gzip.compress(data)
    return len(compressed) / len(data)

def compress_ratio_zlib(data: bytes) -> float:
    """
    Returns compression ratio using zlib (balance).
    """
    if not data:
        return 0.0
    compressed = zlib.compress(data)
    return len(compressed) / len(data)
