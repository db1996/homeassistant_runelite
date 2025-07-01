from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

_LOGGER = logging.getLogger(__name__)

class PlayerSpecialAttack(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS player's special attack."""
    def __init__(self, username: str):
        self._username = username
        self._current_special_attack = 100
        self._unique_id = f"runelite_{sanitize(username)}_special_attack"
        self._attr_name = f"Runelite {username} Special Attack"
        self._attr_unique_id = self._unique_id
        self._attr_unit_of_measurement = "%"
        self._attr_state_class = "total"

    @property
    def state(self):
        return self._current_special_attack
    
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
            "current_special_attack": self._current_special_attack
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._current_special_attack = last_state.attributes.get("current_special_attack")

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._current_special_attack = data.get("current_special_attack", self._current_special_attack)
        self.async_schedule_update_ha_state()
