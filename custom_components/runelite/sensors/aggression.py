from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

class AgressionSensor(SensorEntity, RestoreEntity):
    """Representation of aggression status for a specific user."""

    def __init__(self, username: str) -> None:
        super().__init__()
        self._username = username
        self._unique_id = f"runelite_{sanitize(username)}_aggression"
        self._name = f"Runelite {username} Aggression"
        self._status = None
        self._seconds = 0
        self._ticks = 0

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
            "seconds": self._seconds,
            "ticks": self._ticks,
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
    
    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._status = data.get("status", self._status)
        self._seconds = data.get("seconds", self._seconds)
        self._ticks = data.get("ticks", self._ticks)
        self.async_schedule_update_ha_state()
