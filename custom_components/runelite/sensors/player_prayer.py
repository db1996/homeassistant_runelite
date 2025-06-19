from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging
from ..helpers import sanitize

_LOGGER = logging.getLogger(__name__)

class PlayerPrayer(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS player's prayer."""
    def __init__(self, username: str, max_prayer: int):
        self._username = username
        self._current_prayer = max_prayer
        self._max_prayer = max_prayer
        self._unique_id = f"runelite_{sanitize(username)}_prayer"
        self._attr_name = f"Runelite {username} Prayer"
        self._attr_unique_id = self._unique_id
        self._attr_unit_of_measurement = "Pts"
        self._attr_state_class = "total"

    @property
    def state(self):
        return self._current_prayer
    
    @property
    def extra_state_attributes(self):
        return {
            "current_prayer": self._current_prayer
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._current_prayer = last_state.attributes.get("current_prayer")

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._current_prayer = data.get("current_prayer", self._current_prayer)
        self.async_schedule_update_ha_state()
