from __future__ import annotations

from datetime import timezone, tzinfo

from .csv_ingestion import CsvColumnMapping, CsvIngestionConfig
from .models import SourceMetadata
from .normalisation import (
    DEFAULT_MISSING_VALUES,
    standard_exercise_style_value_map,
    standard_option_type_value_map,
)


def cboe_option_intervals_csv_config(
    source_metadata: SourceMetadata | None = None,
    assume_timezone: tzinfo = timezone.utc,
    include_open_interest: bool = True,
    include_calculated_underlying: bool = True,
) -> CsvIngestionConfig:
    return CsvIngestionConfig(
        mapping=CsvColumnMapping(
            underlying_symbol="Underlying Symbol",
            expiration="Expiration",
            strike="Strike",
            option_type="Option Type",
            quote_timestamp="Quote Datetime",
            bid="Bid",
            ask="Ask",
            bid_size="Bid Size",
            ask_size="Ask Size",
            open_interest="Open Interest" if include_open_interest else None,
            underlying_price=(
                "Active Underlying Price"
                if include_calculated_underlying
                else None
            ),
            underlying_bid="Underlying Bid",
            underlying_ask="Underlying Ask",
        ),
        source_metadata=source_metadata,
        missing_values=DEFAULT_MISSING_VALUES,
        option_type_values=standard_option_type_value_map(),
        exercise_style_values=standard_exercise_style_value_map(),
        assume_timezone=assume_timezone,
    )
