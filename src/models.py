from pydantic import BaseModel
from typing import Literal


class Collections(BaseModel):
    data_source: Literal["transcripts", "press_releases"]


class Period(BaseModel):
    period: Literal[
        "Q1_FY2025-26", "Q1_FY2024-25", "Q2_FY2024-25", "Q3_FY2024-25", "Q4_FY2024-25"
    ]
