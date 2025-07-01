from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

_LOGGER = logging.getLogger(__name__)

class PlayerStatus(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS player's health."""
    def __init__(self, username: str):
        self._username = username
        self._is_online = False
        self._world = None
        self._unique_id = f"runelite_{sanitize(username)}_player_status"
        self._attr_name = f"Runelite {username} Player Status"
        self._attr_unique_id = self._unique_id

    @property
    def state(self):
        return self._is_online
    
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
            "is_online": self._is_online,
            "world": self._world,
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._is_online = last_state.attributes.get("is_online", False)
            self._world = last_state.attributes.get("world", None)

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._is_online = data.get("is_online", self._is_online)
        self._world = data.get("world", self._world)
        self.async_schedule_update_ha_state()
