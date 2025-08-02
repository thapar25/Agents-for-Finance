from typing import Literal, List, Optional
from pydantic import BaseModel, Field


Collection = Literal["transcripts", "reports"]

Quarters = Literal[
    "Q1_FY2025-26",
    "Q1_FY2024-25",
    "Q2_FY2024-25",
    "Q3_FY2024-25",
    "Q4_FY2024-25",
]


class ChatRequest(BaseModel):
    session_id: str = "dev"
    user_message: str


class OtherNotableMetric(BaseModel):
    metric: str
    trendDescription: str


class KeyFinancialTrends(BaseModel):
    totalRevenueTrend: Optional[str] = Field(
        None, description="Trend description for total revenue."
    )
    netProfitTrend: Optional[str] = Field(
        None, description="Trend description for net profit."
    )
    operatingMarginTrend: Optional[str] = Field(
        None, description="Trend description for operating margin."
    )
    otherNotableMetrics: Optional[List[OtherNotableMetric]] = Field(
        default_factory=list,
        description="Additional financial metrics and their trends.",
    )


class ManagementOutlook(BaseModel):
    sentiment: Literal["Positive", "Neutral", "Negative"] = Field(
        ..., description="Overall sentiment tone from management."
    )
    summaryStatements: List[str] = Field(
        ...,
        description="Key forward-looking or strategic statements made by management.",
    )


class FinancialForecast(BaseModel):
    forecastSummary: str = Field(..., description="Narrative summary of the forecast.")
    keyFinancialTrends: KeyFinancialTrends = Field(
        ..., description="Trends in core financial metrics."
    )
    managementOutlook: ManagementOutlook = Field(
        ..., description="Outlook and sentiment from management."
    )
    recurringThemes: List[str] = Field(
        ..., description="Themes repeatedly mentioned in earnings calls."
    )
    risks: List[str] = Field(..., description="Identified business or macro risks.")
    opportunities: List[str] = Field(
        ..., description="Identified growth or operational opportunities."
    )
