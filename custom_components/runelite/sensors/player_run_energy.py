from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging
from ..helpers import sanitize

_LOGGER = logging.getLogger(__name__)

class PlayerRunEnergy(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS player's run energy."""
    def __init__(self, username: str):
        self._username = username
        self._current_run_energy = 100
        self._unique_id = f"runelite_{sanitize(username)}_run_energy"
        self._attr_name = f"Runelite {username} Run Energy"
        self._attr_unique_id = self._unique_id
        self._attr_unit_of_measurement = "%"
        self._attr_state_class = "total"

    @property
    def state(self):
        return self._current_run_energy
    
    @property
    def extra_state_attributes(self):
        return {
            "current_run_energy": self._current_run_energy
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._current_run_energy = last_state.attributes.get("current_run_energy")

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._current_run_energy = data.get("current_run_energy", self._current_run_energy)
        self.async_schedule_update_ha_state()
