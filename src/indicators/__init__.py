"""
Kuiper V2 - Technical Indicators
================================

All 159 TA-Lib indicators organized by category.
"""

from .overlap_studies import (
    compute_overlap_studies,
    OverlapStudiesResult,
    get_overlap_studies_dict,
    MA_TYPE_SMA,
    MA_TYPE_EMA,
    MA_TYPE_WMA,
    MA_TYPE_DEMA,
    MA_TYPE_TEMA,
    MA_TYPE_TRIMA,
    MA_TYPE_KAMA,
    MA_TYPE_MAMA,
    MA_TYPE_T3,
)

__all__ = [
    # Overlap Studies
    'compute_overlap_studies',
    'OverlapStudiesResult',
    'get_overlap_studies_dict',
    
    # MA Type Constants
    'MA_TYPE_SMA',
    'MA_TYPE_EMA',
    'MA_TYPE_WMA',
    'MA_TYPE_DEMA',
    'MA_TYPE_TEMA',
    'MA_TYPE_TRIMA',
    'MA_TYPE_KAMA',
    'MA_TYPE_MAMA',
    'MA_TYPE_T3',
]
