from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo


class SlayerTaskSensor(SensorEntity, RestoreEntity):
    """Current slayer task, as reported by the RuneLite plugin.

    The plugin reads this from RuneLite's own Slayer plugin, so the counts stay
    in step with the in-game task without this integration having to know
    anything about monsters.
    """

    def __init__(self, username: str) -> None:
        super().__init__()
        self._username = username
        self._attr_unique_id = sanitize(f"runelite_{username}_slayer_task")
        self._attr_name = "Slayer task"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:skull-crossbones"
        self._task = None
        self._remaining_amount = 0
        self._initial_amount = 0
        self._task_location = None
        self._streak = 0
        self._points = 0

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def state(self):
        return self._task

    @property
    def extra_state_attributes(self):
        return {
            "task": self._task,
            "remaining_amount": self._remaining_amount,
            "initial_amount": self._initial_amount,
            "task_location": self._task_location,
            "streak": self._streak,
            "points": self._points,
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
            self._task = last_state.attributes.get("task")
            self._remaining_amount = last_state.attributes.get("remaining_amount", 0)
            self._initial_amount = last_state.attributes.get("initial_amount", 0)
            self._task_location = last_state.attributes.get("task_location")
            self._streak = last_state.attributes.get("streak", 0)
            self._points = last_state.attributes.get("points", 0)

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._task = data.get("task", self._task)
        self._remaining_amount = data.get("remaining_amount", self._remaining_amount)
        self._initial_amount = data.get("initial_amount", self._initial_amount)
        self._task_location = data.get("task_location", self._task_location)
        self._streak = data.get("streak", self._streak)
        self._points = data.get("points", self._points)
        self.async_schedule_update_ha_state()
