from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

INVENTORY_SLOTS = 28


class InventorySensor(SensorEntity, RestoreEntity):
    """What the player is carrying, as reported by the RuneLite plugin.

    The state is the number of used slots, so "inventory full" is simply
    state == 28 -- or the `full` attribute, for automations that would rather
    not know the number.
    """

    def __init__(self, username: str) -> None:
        super().__init__()
        self._username = username
        self._attr_unique_id = sanitize(f"runelite_{username}_inventory")
        self._attr_name = "Inventory"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:bag-personal"
        self._attr_native_unit_of_measurement = "slots"
        self._items = []
        self._used_slots = 0

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def state(self):
        return self._used_slots

    @property
    def extra_state_attributes(self):
        return {
            "items": self._items,
            "used_slots": self._used_slots,
            "free_slots": INVENTORY_SLOTS - self._used_slots,
            "total_slots": INVENTORY_SLOTS,
            "full": self._used_slots >= INVENTORY_SLOTS,
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
            self._items = last_state.attributes.get("items", []) or []
            self._used_slots = last_state.attributes.get("used_slots", len(self._items))

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        if "items" in data:
            self._items = data["items"]
            # used_slots travels with the list, but the list is the truth.
            self._used_slots = data.get("used_slots", len(self._items))
        self.async_schedule_update_ha_state()


class EquipmentSensor(SensorEntity, RestoreEntity):
    """What the player is wearing, per equipment slot.

    The state is the weapon's name, which is the slot most worth glancing at;
    everything else is in the `worn` attribute, keyed by slot.
    """

    def __init__(self, username: str) -> None:
        super().__init__()
        self._username = username
        self._attr_unique_id = sanitize(f"runelite_{username}_equipment")
        self._attr_name = "Equipment"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:sword"
        self._worn = {}

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def state(self):
        weapon = self._worn.get("weapon") if isinstance(self._worn, dict) else None
        return weapon.get("name") if isinstance(weapon, dict) else "None"

    @property
    def extra_state_attributes(self):
        return {
            "worn": self._worn,
            "count": len(self._worn),
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
            self._worn = last_state.attributes.get("worn", {}) or {}

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        if "worn" in data:
            self._worn = data["worn"]
        self.async_schedule_update_ha_state()
