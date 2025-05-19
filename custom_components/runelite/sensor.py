"""Sensor platform for RuneLite Farming integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import datetime, timedelta, timezone
from homeassistant.helpers.restore_state import RestoreEntity

from .const import PATCH_TYPE_DATA

DOMAIN = "runelite"
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the RuneLite Farming sensors from a config entry."""
    username = hass.data[DOMAIN][config_entry.entry_id]["username"]

    usernameFixed = username.replace(" ", "_").lower()
    _LOGGER.debug('Setting up sensors for %s', username)
    entities = []
    for patch_type, patch_data in PATCH_TYPE_DATA.items():
        # sanitize the patch type for unique_id
        patch_type = patch_type.replace(" ", "_").lower()
        unique_id = f"runelite_{usernameFixed.lower()}_{patch_type.lower()}_patch"
        _LOGGER.debug('Setting up sensors for %s %s', usernameFixed, unique_id)

        entity = FarmingPatchTypeSensor(username, patch_type, unique_id, patch_data)
        entities.append(entity)

    # Add a generic contract sensor for this username (keeping this for now)
    contract_unique_id = f"runelite_{usernameFixed.lower()}_farming_contract"
    contract_entity = FarmingContractSensor(username, contract_unique_id)
    entities.append(contract_entity)

    birdhouse_unique_id = f"runelite_{usernameFixed.lower()}_birdhouses"
    birdhouse_entity = BirdhousesSensor(username, birdhouse_unique_id)
    entities.append(birdhouse_entity)

    farming_tick_unique_id = f"runelite_{usernameFixed.lower()}_farming_tick_offset"
    farming_tick_entity = FarmingTickOffsetSensor(username, farming_tick_unique_id)
    entities.append(farming_tick_entity)

    async_add_entities(entities)
    _LOGGER.debug('Added %d sensors for %s', len(entities), username)

    if "entities" not in hass.data[DOMAIN][config_entry.entry_id]:
        hass.data[DOMAIN][config_entry.entry_id]["entities"] = {}
    for entity in entities:
        hass.data[DOMAIN][config_entry.entry_id]["entities"][entity.entity_id] = entity



class FarmingPatchTypeSensor(SensorEntity, RestoreEntity):
    """Representation of a specific type of farming patch with its data."""

    def __init__(
        self, username: str, patch_type: str, unique_id: str, patch_data: dict
    ) -> None:
        """Initialize the sensor."""
        self._username = username
        self._patch_type = patch_type
        self._unique_id = unique_id
        self._name = f"Runelite {username} {patch_type} Patch"
        self._cycle_length_minutes = patch_data.get("cycle_length_minutes")
        self._global_cycles = patch_data.get("global_cycles")
        self._growth_ticks = patch_data.get("growth_ticks")
        self._status = None
        self._growth_ticks_days = patch_data.get("growth_ticks_days")
        self._completion_time = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._status

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = {
            "status": self._status,
            "completion_time": self._completion_time,
            "patch_type": self._patch_type,
            "cycle_length_minutes": self._cycle_length_minutes,
        }
        if self._global_cycles is not None:
            attributes["global_cycles"] = self._global_cycles
        if self._growth_ticks is not None:
            attributes["growth_ticks"] = self._growth_ticks
        if self._growth_ticks_days is not None:
            attributes["growth_ticks_days"] = self._growth_ticks_days
        return attributes
    
    async def async_added_to_hass(self) -> None:
        """Restore the last known state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._status = last_state.state
            if "completion_time" in last_state.attributes and last_state.attributes["completion_time"] is not None:
                _LOGGER.info("Restoring completion time: %s", last_state.attributes["completion_time"])
                self._completion_time = datetime.fromisoformat(
                    last_state.attributes["completion_time"]
                ).replace(tzinfo=timezone.utc)

    async def async_update(self) -> None:
        """Fetch new state data for the sensor. (Likely updated externally)."""

    async def update_data(self, data: dict) -> None:
        """Update the sensor's data from external sources."""
        self._completion_time = data.get("completion_time", self._completion_time)
        self._status = data.get("status", self._status)
        self.async_schedule_update_ha_state()


class FarmingContractSensor(SensorEntity, RestoreEntity):
    """Representation of a farming contract for a specific user."""

    def __init__(self, username: str, unique_id: str) -> None:
        """Initialize the sensor."""
        super().__init__()
        self._username = username
        self._unique_id = unique_id
        self._name = f"Runelite {username} Farming Contract"
        self._status = None
        self._completion_time = None
        self._patch_type = None
        self._crop_type = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._status

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "status": self._status,
            "completion_time": self._completion_time,
            "patch_type": self._patch_type,
            "crop_type": self._crop_type,
        }
    async def async_added_to_hass(self) -> None:
        """Restore the last known state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._crop_type = last_state.attributes.get("crop_type")
            self._patch_type = last_state.attributes.get("patch_type")
            self._status = last_state.attributes.get("status")
            if "completion_time" in last_state.attributes and last_state.attributes["completion_time"] is not None:
                try:
                    self._completion_time = datetime.fromisoformat(
                        last_state.attributes["completion_time"]
                    ).replace(tzinfo=timezone.utc)
                except ValueError:
                    self._completion_time = None
    
    async def async_update(self) -> None:
        """Fetch new state data for the sensor. (Likely updated externally)."""

    async def update_data(self, data: dict) -> None:
        """Update the sensor's data from external sources."""
        self._completion_time = data.get("completion_time", self._completion_time)
        self._patch_type = data.get("patch_type", self._patch_type)
        self._crop_type = data.get("crop_type", self._crop_type)
        self._status = data.get("status", self._status)
        self.async_schedule_update_ha_state()

class BirdhousesSensor(SensorEntity, RestoreEntity):
    """Representation of birdhouses status for a specific user."""

    def __init__(self, username: str, unique_id: str) -> None:
        """Initialize the sensor."""
        super().__init__()
        self._username = username
        self._unique_id = unique_id
        self._name = f"Runelite {username} Birdhouses"
        self._status = None
        self._completion_time = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._status

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "status": self._status,
            "completion_time": self._completion_time,
        }
    async def async_added_to_hass(self) -> None:
        """Restore the last known state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._status = last_state.attributes.get("status")
            if "completion_time" in last_state.attributes and last_state.attributes["completion_time"] is not None:
                try:
                    self._completion_time = datetime.fromisoformat(
                        last_state.attributes["completion_time"]
                    ).replace(tzinfo=timezone.utc)
                except ValueError:
                    self._completion_time = None
    
    async def async_update(self) -> None:
        """Fetch new state data for the sensor. (Likely updated externally)."""

    async def update_data(self, data: dict) -> None:
        """Update the sensor's data from external sources."""
        self._completion_time = data.get("completion_time", self._completion_time)
        self._status = data.get("status", self._status)
        self.async_schedule_update_ha_state()

class FarmingTickOffsetSensor(SensorEntity, RestoreEntity):
    """Representation of birdhouses status for a specific user."""

    def __init__(self, username: str, unique_id: str, farming_tick: int = 0) -> None:
        """Initialize the sensor."""
        super().__init__()
        self._username = username
        self._unique_id = unique_id
        self._name = f"Runelite {username} Farming tick offset"
        self._farming_tick_offset = farming_tick

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._farming_tick_offset

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "farming_tick_offset": self._farming_tick_offset,
        }
    async def async_added_to_hass(self) -> None:
        """Restore the last known state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._farming_tick_offset = last_state.attributes.get("farming_tick_offset")
    
    async def async_update(self) -> None:
        """Fetch new state data for the sensor. (Likely updated externally)."""

    async def update_data(self, data: dict) -> None:
        """Update the sensor's data from external sources."""
        self._farming_tick_offset = data.get("farming_tick_offset", self._farming_tick_offset)
        self.async_schedule_update_ha_state()
