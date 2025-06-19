from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from ..helpers import sanitize

class FarmingTickOffsetSensor(SensorEntity, RestoreEntity):
    """Representation of farming tick offset for a specific user."""

    def __init__(self, username: str, farming_tick: int = 0) -> None:
        super().__init__()
        self._username = username
        self._unique_id = f"runelite_{sanitize(username)}_farming_tick_offset"
        self._name = f"Runelite {username} Farming tick offset"
        self._farming_tick_offset = farming_tick

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def state(self):
        return self._farming_tick_offset

    @property
    def extra_state_attributes(self):
        return {
            "farming_tick_offset": self._farming_tick_offset,
        }
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._farming_tick_offset = last_state.attributes.get("farming_tick_offset")
    
    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        self._farming_tick_offset = data.get("farming_tick_offset", self._farming_tick_offset)
        self.async_schedule_update_ha_state()
