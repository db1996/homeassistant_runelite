def sanitize(text: str) -> str:
    """Sanitize the string for use in unique IDs."""
    # replace sensitive characters with underscores and convert to lowercase
    return text.replace(" ", "_").lower()
