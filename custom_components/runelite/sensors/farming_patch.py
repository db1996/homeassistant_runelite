from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from datetime import datetime, timezone
import logging

_LOGGER = logging.getLogger(__name__)

class FarmingPatchTypeSensor(SensorEntity, RestoreEntity):
    """Representation of a specific type of farming patch with its data."""

    def __init__(
        self, username: str, patch_type: str, unique_id: str, patch_data: dict
    ) -> None:
        self._username = username
        self._patch_type = patch_type
        self._unique_id = unique_id
        self._name = f"Runelite {username} {patch_type} Patch"
        self._cycle_length_minutes = patch_data.get("cycle_length_minutes")
        self._global_cycles = patch_data.get("global_cycles")
        self._growth_ticks = patch_data.get("growth_ticks")
        self._status = None
        self._growth_ticks_days = patch_data.get("growth_ticks_days")
        self._completion_time = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def state(self):
        return self._status

    @property
    def extra_state_attributes(self):
        attributes = {
            "status": self._status,
            "completion_time": self._completion_time,
            "patch_type": self._patch_type,
            "cycle_length_minutes": self._cycle_length_minutes,
        }
        if self._global_cycles is not None:
            attributes["global_cycles"] = self._global_cycles
        if self._growth_ticks is not None:
            attributes["growth_ticks"] = self._growth_ticks
        if self._growth_ticks_days is not None:
            attributes["growth_ticks_days"] = self._growth_ticks_days
        return attributes
    
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._status = last_state.state
            if "completion_time" in last_state.attributes and last_state.attributes["completion_time"] is not None:
                _LOGGER.debug("Restoring completion time: %s", last_state.attributes["completion_time"])
                self._completion_time = datetime.fromisoformat(
                    last_state.attributes["completion_time"]
                ).replace(tzinfo=timezone.utc)

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._completion_time = data.get("completion_time", self._completion_time)
        self._status = data.get("status", self._status)
        self.async_schedule_update_ha_state()
