from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging

_LOGGER = logging.getLogger(__name__)

class OsrsActivitySensor(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS activity from the hiscore API."""
    def __init__(self, coordinator, username: str, activity_data: dict, unique_id: str):
        self.coordinator = coordinator
        self._username = username
        self._activity_data = activity_data
        self._unique_id = unique_id
        self._attr_name = f"Runelite {username} Activity {activity_data['name'].capitalize()}"
        self._attr_unique_id = unique_id
        self._attr_unit_of_measurement = "KC"
        self._attr_state_class = "total_increasing"

    @property
    def state(self):
        return self._activity_data['score']
    
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
