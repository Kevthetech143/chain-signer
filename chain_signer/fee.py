"""Our built-in swap fee. Tiny, and configurable in one place.

10 basis points = 0.1% of the swap. Small enough it never stops anyone from using the tool.
"""
DEFAULT_FEE_BPS = 10  # 0.1%


def fee_fraction(bps: int = DEFAULT_FEE_BPS) -> float:
    return bps / 10_000
