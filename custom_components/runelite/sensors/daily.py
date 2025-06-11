from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging

_LOGGER = logging.getLogger(__name__)

class DailySensor(SensorEntity, RestoreEntity):
    """Sensor for a daily task in OSRS."""
    def __init__(self, username: str, name: str, unique_id: str):
        self._task_state = -1
        self._username = username
        self._unique_id = unique_id
        self._attr_name = f"Runelite {username} Daily {name.capitalize()}"
        self._attr_unique_id = unique_id

    @property
    def state(self):
        return self._task_state

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