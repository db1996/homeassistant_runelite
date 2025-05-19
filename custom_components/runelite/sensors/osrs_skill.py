from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging

_LOGGER = logging.getLogger(__name__)

class OsrsSkillSensor(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS skill from the hiscore API."""
    def __init__(self, coordinator, username: str, skill_data: dict, unique_id: str):
        self.coordinator = coordinator
        self._username = username
        self._skill_data = skill_data
        self._unique_id = unique_id
        self._attr_name = f"OSRS {username} {skill_data['name'].capitalize()}"
        self._attr_unique_id = unique_id

    @property
    def state(self):
        return self._skill_data['xp']
    
    @property
    def extra_state_attributes(self):
        return self._skill_data

    async def async_update(self):
        # Update the skill data from the latest coordinator data
        skills = self.coordinator.data.get("skills", [])
        for skill in skills:
            if skill.get("id") == self._skill_data.get('id'):
                self._skill_data = skill
                break

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
