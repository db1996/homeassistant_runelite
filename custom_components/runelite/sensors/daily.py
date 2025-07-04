from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

_LOGGER = logging.getLogger(__name__)

class DailySensor(SensorEntity, RestoreEntity):
    """Sensor for a daily task in OSRS."""
    def __init__(self, username: str, name: str):
        self._task_state = -1
        self._username = username
        self._unique_id = sanitize(f"runelite_{username}_daily_{name}")
        self._attr_name = f"Runelite {username} Daily {name.capitalize()}"
        self._attr_unique_id = self._unique_id
        self._attr_unit_of_measurement = "Done"

    @property
    def state(self):
        return self._task_state
    
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
            self._task_state = last_state.state
    
    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        if "task_state" in data:
            self._task_state = data.get("task_state", self._task_state)
        if "status" in data:
            self._task_state = data.get("status", self._task_state)
        if "state" in data:
            self._task_state = data.get("state", self._task_state)
            
        self.async_schedule_update_ha_state()