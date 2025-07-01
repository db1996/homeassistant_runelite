from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from datetime import datetime, timezone
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

class BirdhousesSensor(SensorEntity, RestoreEntity):
    """Representation of birdhouses status for a specific user."""

    def __init__(self, username: str) -> None:
        super().__init__()
        self._username = username
        self._unique_id = f"runelite_{sanitize(username)}_birdhouses"
        self._name = f"Runelite {username} Birdhouses"
        self._status = None
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
        return {
            "status": self._status,
            "completion_time": self._completion_time,
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
            self._status = last_state.attributes.get("status")
            if "completion_time" in last_state.attributes and last_state.attributes["completion_time"] is not None:
                try:
                    self._completion_time = datetime.fromisoformat(
                        last_state.attributes["completion_time"]
                    ).replace(tzinfo=timezone.utc)
                except ValueError:
                    self._completion_time = None
    
    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._completion_time = data.get("completion_time", self._completion_time)
        self._status = data.get("status", self._status)
        self.async_schedule_update_ha_state()
