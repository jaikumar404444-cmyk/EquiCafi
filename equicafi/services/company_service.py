from __future__ import annotations

from equicafi.models import CompanyProfile, DataQuality
from equicafi.providers import provider_for


class CompanyService:
    """Retrieves a company profile plus source metadata without brittle assumptions."""

    def profile(self, ticker: str) -> tuple[CompanyProfile, DataQuality]:
        provider = provider_for(ticker)
        data = provider.fetch(ticker)
        profile = CompanyProfile(
            ticker=data.ticker,
            name=data.company_name or data.ticker,
            exchange=data.exchange,
            sector=data.sector,
            industry=data.industry,
            currency=data.currency,
            website=data.website,
        )
        notes = []
        if data.synthetic:
            notes.append("Synthetic demonstration data; not live company data.")
        if data.company_name == data.ticker and not data.synthetic:
            notes.append("Provider profile name was unavailable; ticker symbol is used as the display name.")
        quality = "high"
        if data.annual_financials.empty or data.balance_sheet.empty:
            quality = "medium"
            notes.append("One or more annual financial statement datasets were unavailable.")
        if data.price_history.empty:
            quality = "medium"
            notes.append("Historical market-price data was unavailable or incomplete.")
        return profile, DataQuality(
            source=data.source,
            status="synthetic demo data" if data.synthetic else "provider data",
            quality=quality,
            notes=notes,
        )
