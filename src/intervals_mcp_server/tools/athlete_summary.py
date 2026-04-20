"""
Athlete summary MCP tool for Intervals.icu.

This module contains a tool for retrieving weekly athlete summary data.
"""

import json
from typing import Any

from intervals_mcp_server.api.client import make_intervals_request
from intervals_mcp_server.config import get_config
from intervals_mcp_server.mcp_instance import mcp
from intervals_mcp_server.utils.validation import resolve_athlete_id, validate_date

config = get_config()


@mcp.tool()
async def get_athlete_summary(
    start_date: str,
    end_date: str,
    athlete_id: str | None = None,
    api_key: str | None = None,
    tags: str | None = None,
) -> str:
    """Get the Intervals.icu athlete summary JSON for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        athlete_id: The Intervals.icu athlete ID (optional, will use ATHLETE_ID from .env if not provided)
        api_key: The Intervals.icu API key (optional, will use API_KEY from .env if not provided)
        tags: Optional comma-separated athlete tags to filter the summary
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    try:
        start_date = validate_date(start_date)
        end_date = validate_date(end_date)
    except ValueError as exc:
        return f"Error: {exc}"

    params: dict[str, Any] = {"start": start_date, "end": end_date}
    if tags:
        params["tags"] = tags

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/athlete-summary",
        api_key=api_key,
        params=params,
    )

    if isinstance(result, dict) and "error" in result:
        error_message = result.get("message", "Unknown error")
        return f"Error fetching athlete summary: {error_message}"

    if not result:
        return (
            f"No athlete summary found for athlete {athlete_id_to_use} "
            "in the specified date range."
        )

    return json.dumps(result, indent=2)
