from typing import Literal, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import date



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


class EPS(BaseModel):
    """Earnings per share details, including basic and diluted EPS."""

    basic: Optional[float] = Field(None, description="Basic earnings per share")
    diluted: Optional[float] = Field(None, description="Diluted earnings per share")
    commentary: Optional[str] = Field(
        None, description="Any narrative about EPS changes or drivers"
    )


class NetProfit(BaseModel):
    """Net profit amount and its margin representation."""

    value: Optional[float] = Field(None, description="Net profit in monetary units")
    margin: Optional[float] = Field(
        None, description="Net profit as a percentage of revenue"
    )


class OperatingMargin(BaseModel):
    """Operating margin insights, including trend and cost pressures."""

    value: Optional[float] = Field(
        None, description="Operating margin as a decimal (e.g. 0.15 for 15%)"
    )
    trend: Optional[str] = Field(
        None, description="Narrative about margin trend over time"
    )
    pressure_factors: Optional[str] = Field(
        None, description="Cost or market dynamics impacting margin"
    )


class TotalRevenue(BaseModel):
    """Total revenue for the period with comparative growth."""

    value: Optional[float] = Field(None, description="Total revenue in monetary units")
    yoy_growth: Optional[float] = Field(
        None, description="Year-over-year revenue growth rate"
    )
    qoq_growth: Optional[float] = Field(
        None, description="Quarter-over-quarter revenue growth rate"
    )
    seasonal_commentary: Optional[str] = Field(
        None, description="Notes on seasonal trends or anomalies"
    )


class SegmentPerformanceItem(BaseModel):
    """Breakdown of revenue and growth for an individual segment."""

    segment: str = Field(..., description="Name of the business segment")
    revenue: Optional[float] = Field(None, description="Segment revenue")
    growth: Optional[float] = Field(None, description="Segment growth rate")
    commentary: Optional[str] = Field(
        None, description="Segment-specific insights or issues"
    )


class ManagementSentiment(BaseModel):
    """Tone and posture of leadership, often inferred from calls or letters."""

    tone: Optional[str] = Field(
        None, description="Overall sentiment (e.g., confident, cautious, bullish)"
    )
    quotes: List[str] = Field(
        default_factory=list, description="Relevant excerpts from leadership"
    )
    confidence_rating: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Normalized confidence level from 0 (low) to 1 (high)",
    )


class ForwardGuidance(BaseModel):
    """Company outlook and expectations, qualitative and quantitative."""

    revenue_range: Optional[Tuple[Optional[float], Optional[float]]] = Field(
        None, description="Forecasted revenue range"
    )
    eps_range: Optional[Tuple[Optional[float], Optional[float]]] = Field(
        None, description="Expected EPS range"
    )
    strategic_direction: Optional[str] = Field(
        None, description="Narrative on company focus and direction"
    )
    macroeconomic_assumptions: Optional[str] = Field(
        None, description="Underlying assumptions like interest rates"
    )


class MarketSentiment(BaseModel):
    """Sentiment from analysts, press, and general public."""

    analyst_opinion: Optional[str] = Field(
        None, description="Wall Street or institutional sentiment"
    )
    media_coverage: Optional[str] = Field(None, description="Tone of media coverage")
    public_reception: Optional[str] = Field(
        None, description="Customer or retail investor response"
    )


class CompetitionItem(BaseModel):
    """Peer comparison on product, strategy, or performance."""

    competitor: str = Field(..., description="Name of the competing company")
    comparison: Optional[str] = Field(
        None, description="How the subject company stacks up"
    )


class ExecutiveSummary(BaseModel):
    """Top-level overview of key takeaways for fast digestion."""

    key_highlights: List[str] = Field(
        default_factory=list, description="Bullet points of major insights"
    )
    top_line_results: NetProfit = Field(
        ..., description="Headline profitability metrics"
    )
    forward_guidance_summary: Optional[str] = Field(
        None, description="Concise outlook message"
    )


class RevenueOverview(BaseModel):
    """In-depth revenue analysis across the business and its segments."""

    total_revenue: TotalRevenue = Field(
        ..., description="Total revenue data with growth"
    )
    segment_performance: List[SegmentPerformanceItem] = Field(
        default_factory=list, description="Breakdown by segment or geography"
    )


class Profitability(BaseModel):
    """Profitability metrics including operating margin and EPS."""

    operating_margin: OperatingMargin = Field(
        ..., description="Operating efficiency and trends"
    )
    net_profit: NetProfit = Field(..., description="Bottom-line performance")
    eps: EPS = Field(..., description="Earnings per share details")


class StrategicInsights(BaseModel):
    """Qualitative and strategic observations from recurring signals."""

    recurring_themes: List[str] = Field(
        default_factory=list, description="Repeated business themes or risks"
    )
    notable_initiatives: List[str] = Field(
        default_factory=list, description="New or ongoing major projects"
    )
    management_sentiment: ManagementSentiment = Field(
        ..., description="Leadership tone and outlook"
    )


class MarketLandscape(BaseModel):
    """How the company is perceived externally and who it's competing with."""

    market_sentiment: MarketSentiment = Field(
        ..., description="Market reception and opinion"
    )
    competition: List[CompetitionItem] = Field(
        default_factory=list, description="Competitive landscape details"
    )


class RisksAndFlags(BaseModel):
    """All meaningful risks and red flags worth surfacing."""

    operational_risks: List[str] = Field(
        default_factory=list, description="Internal or execution risks"
    )
    financial_flags: List[str] = Field(
        default_factory=list, description="Potential concerns in financials"
    )
    external_threats: List[str] = Field(
        default_factory=list, description="Macro, legal, or regulatory risks"
    )


class QualitativeForecast(BaseModel):
    key_trends: List[str] = Field(
        default_factory=list, description="Summarized financial or strategic trends"
    )
    upcoming_opportunities: List[str] = Field(
        default_factory=list, description="Major growth levers"
    )
    upcoming_risks: List[str] = Field(
        default_factory=list, description="Known or potential threats"
    )
    analyst_forecast_summary: Optional[str] = Field(
        None, description="Narrative paragraph summarizing the forecast"
    )


class FinancialForecastReport(BaseModel):
    """Top-level financial forecast report for a company in a given period."""

    report_date: date = Field(..., description="Date the report is generated")
    company: str = Field(..., description="Name of the company being reported on")
    ticker: str = Field(..., description="Public stock ticker symbol")
    fiscal_period: str = Field(..., description="Reporting period (e.g., Q2 2025)")

    executive_summary: ExecutiveSummary = Field(..., description="High-level takeaways")
    revenue_overview: RevenueOverview = Field(..., description="Revenue breakdown")
    profitability: Profitability = Field(
        ..., description="Detailed financial performance"
    )
    strategic_insights: StrategicInsights = Field(
        ..., description="Qualitative business observations"
    )
    outlook: ForwardGuidance = Field(
        ..., description="Forward-looking statements and targets"
    )
    market_landscape: MarketLandscape = Field(
        ..., description="Sentiment and competition analysis"
    )
    risks_and_flags: RisksAndFlags = Field(
        ..., description="Risk exposure and warnings"
    )
    qualitative_forecast: Optional[QualitativeForecast] = Field(
        None, description="Qualitative insights and analyst forecast summary"
    )
    sources: List[str] = Field(
        default_factory=list, description="Cited data sources and references"
    )


class ForecastResponse(BaseModel):
    forecast: Optional[FinancialForecastReport] = None
    error: Optional[str] = None
