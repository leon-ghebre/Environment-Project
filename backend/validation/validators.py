"""
validators.py

Input validation functions for all API endpoints.
"""


def validate_site_id(site_code: str | None, valid_site_codes: list) -> str | None:
    """Validates that a site_code is present and exists in the dataset.

    Args:
        site_code: The site_code value from the request query parameters.
        valid_site_codes: List of site_codes that exist in the database.

    Returns:
        An error message string if validation fails, or None if valid.
    """
    if not site_code:
        return "site_code is required"
    if site_code not in valid_site_codes:
        return f"invalid site_code: {site_code}"
    return None
