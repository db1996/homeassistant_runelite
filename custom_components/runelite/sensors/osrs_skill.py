from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging
from ..helpers import sanitize

_LOGGER = logging.getLogger(__name__)

class OsrsSkillSensor(SensorEntity, RestoreEntity):
    """Sensor for a single OSRS skill from the hiscore API."""
    def __init__(self, coordinator, username: str, skill_data: dict):
        self.coordinator = coordinator
        self._username = username
        self._skill_data = skill_data
        self._skill_id = skill_data.get('id', 0)
        self._skill_xp = skill_data.get('xp', 0)
        self._skill_level = skill_data.get('level', 1)
        self._skill_virtual_level = skill_data.get('level', 1)
        self._skill_rank = skill_data.get('rank', 0)
        self._skill_name = skill_data.get('name', None)
        self._unique_id = sanitize(f"runelite_{username}_skill_{skill_data['name']}")
        self._attr_name = f"Runelite {username} Skill {skill_data['name'].capitalize()}"
        self._attr_unique_id = self._unique_id
        self._attr_unit_of_measurement = "XP"
        self._attr_state_class = "total_increasing"

    @property
    def state(self):
        return self._skill_data['xp']
    
    @property
    def extra_state_attributes(self):
        return {
            "id": self._skill_id,
            "name": self._skill_name,
            "level": self._skill_level,
            "virtual_level": self._skill_virtual_level,
            "xp": self._skill_xp,
            "rank": self._skill_rank,
        }

    async def async_update(self):
        # Update the skill data from the latest coordinator data
        skills = self.coordinator.data.get("skills", [])
        for skill in skills:
            if skill.get("id") == self._skill_id:
                self._skill_xp = skill.get("xp", self._skill_xp)
                self._skill_level = skill.get("level", self._skill_level)
                self._skill_rank = skill.get("rank", self._skill_rank)
                self._skill_name = skill.get("name", self._skill_name)
                break

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    
    async def update_data(self, data: dict) -> None:
        self._skill_virtual_level = data.get("virtual_level", self._skill_virtual_level)
        self.async_schedule_update_ha_state()
