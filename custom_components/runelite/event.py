"""Event platform for the RuneLite integration."""

from __future__ import annotations

from homeassistant.components.event import EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, EVENT_ENTITIES
from .helpers import sanitize


def event_unique_id(username: str, key: str) -> str:
    return sanitize(f"runelite_{username}_{key}_event")


class RuneliteEventEntity(EventEntity):
    """Shows up in the automation editor, so the plugin's events can be picked as triggers."""

    def __init__(self, username: str, key: str, name: str, icon: str, event_types: list[str]) -> None:
        super().__init__()
        self._username = username
        self._attr_unique_id = event_unique_id(username, key)
        self._attr_name = name
        self._attr_has_entity_name = True
        self._attr_icon = icon
        self._attr_event_types = event_types

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, sanitize(self._username))},
            name=f"RuneLite ({self._username})",
            manufacturer="RuneLite",
            model="Old School RuneScape",
            entry_type=None,
        )

    def fire(self, event_type: str, data: dict) -> None:
        self._trigger_event(event_type, data)
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the RuneLite event entities from a config entry."""
    username = hass.data[DOMAIN][config_entry.entry_id]["username"]
    entities = [
        RuneliteEventEntity(username, key, name, icon, event_types)
        for key, (name, icon, event_types) in EVENT_ENTITIES.items()
    ]
    async_add_entities(entities)

    entities_map = hass.data[DOMAIN][config_entry.entry_id].setdefault("entities", {})
    for entity in entities:
        entities_map[entity.unique_id] = entity
