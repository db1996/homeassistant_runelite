from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

_LOGGER = logging.getLogger(__name__)

class PlayerStatusEffects(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS player's status effects."""
    def __init__(self, username: str):
        self._username = username
        self._current_status_effects = []
        self._unique_id = f"runelite_{sanitize(username)}_status_effects"
        self._attr_name = f"Runelite {username} Status Effects"
        self._attr_unique_id = self._unique_id
        self._attr_unit_of_measurement = "%"
        self._attr_state_class = "total"

    @property
    def state(self):
        return self._current_status_effects
    
    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, sanitize(self._username))},
            name=f"RuneLite ({self._username})",
            manufacturer="RuneLite",
            model="Old School RuneScape",
            entry_type=None,  # Could be "service" or "gateway", but None is fine for a player
        )
    
    @property
    def extra_state_attributes(self):
        return {
            "current_status_effects": self._current_status_effects
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._current_status_effects = last_state.attributes.get("current_status_effects")

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._current_status_effects = data.get("current_status_effects", self._current_status_effects)
        self.async_schedule_update_ha_state()
