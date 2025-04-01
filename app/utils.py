from typing import Any, Optional, get_type_hints


def require_setting(settings: Any, setting_name: str) -> Any:
    """
    Ensures that a setting is present and not None, unless it's Optional.
    Raises ValueError if the setting is missing and not Optional.
    """
    setting_value = getattr(settings, setting_name, None)
    type_hints = get_type_hints(settings)
    setting_type = type_hints.get(setting_name)

    if setting_type is not Optional and setting_value is None:
        raise ValueError(f"Setting '{setting_name}' is required but not set.")
    return setting_value
