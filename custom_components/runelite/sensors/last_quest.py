from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo


class LastQuestSensor(SensorEntity, RestoreEntity):
    """The quest whose progress moved most recently."""

    def __init__(self, username: str) -> None:
        super().__init__()
        self._username = username
        self._attr_unique_id = sanitize(f"runelite_{username}_last_quest")
        self._attr_name = "Last quest"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:script-text"
        self._quest = None
        self._state_value = None
        self._stage = 0
        self._quest_points = 0
        self._completed = 0
        self._total = 0

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def state(self):
        return self._quest

    @property
    def extra_state_attributes(self):
        return {
            "quest": self._quest,
            "state": self._state_value,
            "stage": self._stage,
            "quest_points": self._quest_points,
            "completed": self._completed,
            "total": self._total,
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, sanitize(self._username))},
            name=f"RuneLite ({self._username})",
            manufacturer="RuneLite",
            model="Old School RuneScape",
            entry_type=None,
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._quest = last_state.attributes.get("quest")
            self._state_value = last_state.attributes.get("state")
            self._stage = last_state.attributes.get("stage", 0)
            self._quest_points = last_state.attributes.get("quest_points", 0)
            self._completed = last_state.attributes.get("completed", 0)
            self._total = last_state.attributes.get("total", 0)

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._quest = data.get("quest", self._quest)
        self._state_value = data.get("state", self._state_value)
        self._stage = data.get("stage", self._stage)
        self._quest_points = data.get("quest_points", self._quest_points)
        self._completed = data.get("completed", self._completed)
        self._total = data.get("total", self._total)
        self.async_schedule_update_ha_state()
