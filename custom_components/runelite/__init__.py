"""The RuneLite Farming integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .services import RuneLiteFarmingServices  # Import the service registration function
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

DOMAIN = "runelite"
PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RuneLite Farming from a config entry."""
    username = entry.data["username"]
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"username": username, "entities": {}} # Initialize entities

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    RuneLiteFarmingServices(hass, entry)  # Register the services

    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))

    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the RuneLite Farming component (for YAML import)."""
    if DOMAIN in config:
        for entry_config in config[DOMAIN]:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": "import"}, data=entry_config
                )
            )
    return True