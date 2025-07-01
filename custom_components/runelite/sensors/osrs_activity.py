from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

_LOGGER = logging.getLogger(__name__)

class OsrsActivitySensor(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS activity from the hiscore API."""
    def __init__(self, coordinator, username: str, activity_data: dict):
        self.coordinator = coordinator
        self._username = username
        self._activity_data = activity_data
        self._unique_id = sanitize(f"runelite_{username}_activity_{activity_data['name']}")
        self._attr_name = f"Runelite {username} Activity {activity_data['name'].capitalize()}"
        self._attr_unique_id = self._unique_id
        self._attr_unit_of_measurement = "KC"
        self._attr_state_class = "total"

    @property
    def state(self):
        return self._activity_data['score']
    
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
        return self._activity_data

    async def async_update(self):
        # Update the activity data from the latest coordinator data
        activities = self.coordinator.data.get("activities", [])
        for activity in activities:
            if activity.get("id") == self._activity_data.get('id'):
                self._activity_data = activity
                break

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
