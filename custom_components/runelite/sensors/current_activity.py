from homeassistant.components.sensor import SensorEntity
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo


class CurrentActivitySensor(SensorEntity):
    """The skill the player is working on right now, read from their animation.

    State is the skill's name in lowercase ("mining", "fishing", ...) or "none".
    Not restored across a restart on purpose: an activity from before the
    restart is almost certainly over, and the plugin sends the current one
    again as soon as it changes or the player logs in.
    """

    def __init__(self, username: str) -> None:
        super().__init__()
        self._username = username
        self._attr_unique_id = sanitize(f"runelite_{username}_activity")
        self._attr_name = "Current activity"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:pickaxe"
        self._activity = None

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def state(self):
        return self._activity

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, sanitize(self._username))},
            name=f"RuneLite ({self._username})",
            manufacturer="RuneLite",
            model="Old School RuneScape",
            entry_type=None,
        )

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        if "activity" in data:
            self._activity = data["activity"]
        self.async_schedule_update_ha_state()
