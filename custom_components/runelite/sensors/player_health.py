from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

_LOGGER = logging.getLogger(__name__)

class PlayerHealth(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS player's health."""
    def __init__(self, username: str, max_health: int):
        self._username = username
        self._current_health = max_health
        self._max_health = max_health
        self._unique_id = f"runelite_{sanitize(username)}_health"
        self._attr_name = f"Runelite {username} Health"
        self._attr_unique_id = self._unique_id
        self._attr_unit_of_measurement = "HP"
        self._attr_state_class = "total"

    @property
    def state(self):
        return self._current_health

    @property
    def extra_state_attributes(self):
        return {
            "current_health": self._current_health,
            "max_health": self._max_health,
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, sanitize(self._username))},
            name=f"RuneLite ({self._username})",
            manufacturer="RuneLite",
            model="Old School RuneScape",
            entry_type=None,  # Could be "service" or "gateway", but None is fine for a player
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._current_health = last_state.attributes.get("current_health", self._current_health)

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._current_health = data.get("current_health", self._current_health)
        self.async_schedule_update_ha_state()
