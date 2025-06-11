"""Sensor platform for RuneLite Farming integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import PATCH_TYPE_DATA, DAILY_SENSORS
from .sensors.osrs_skill import OsrsSkillSensor
from .sensors.osrs_activity import OsrsActivitySensor
from .sensors.daily import DailySensor
from .sensors.farming_patch import FarmingPatchTypeSensor
from .sensors.contract import FarmingContractSensor
from .sensors.birdhouses import BirdhousesSensor
from .sensors.farming_tick import FarmingTickOffsetSensor
from .sensors.compost_bin import CompostBinSensor

DOMAIN = "runelite"
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the RuneLite Farming sensors from a config entry."""
    username = hass.data[DOMAIN][config_entry.entry_id]["username"]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    if not coordinator or not coordinator.data:
        _LOGGER.error("No data available for %s", username)
        return
    
    # create skills sensors
    entities = []

    # Example: create a sensor for each skill in the hiscore data
    if coordinator.data:
        for skill in coordinator.data.get("skills", []):
            skill_name = skill.get('name').lower()
            if skill_name in ["overall"]:
                skill_name = "total"  # Normalize the name for the total skill

            skill['name'] = skill_name.capitalize()  # Capitalize the skill name for display
                
            skill_entity = OsrsSkillSensor(
                coordinator,
                username,
                skill,
                f"runelite_{username.lower()}_skill_{skill_name}",
            )
            entities.append(skill_entity)
        for activity in coordinator.data.get("activities", []):
            activity_name = activity.get('name').lower()
            activity['name'] = activity_name.capitalize()  # Capitalize the activity name for display
            activity_entity = OsrsActivitySensor(
                coordinator,
                username,
                activity,
                f"runelite_{username.lower()}_activity_{activity_name}",
            )
            _LOGGER.debug('Adding activity sensor for %s: %s', username, activity_name)
            entities.append(activity_entity)


    usernameFixed = username.replace(" ", "_").lower()
    _LOGGER.debug('Setting up sensors for %s', username)
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

    big_compost_unique_id = f"runelite_{usernameFixed.lower()}_big_compost"
    big_compost_entity = CompostBinSensor(username, big_compost_unique_id, f"Runelite {usernameFixed.lower()} Big Compost")
    entities.append(big_compost_entity)

    farming_tick_unique_id = f"runelite_{usernameFixed.lower()}_farming_tick_offset"
    farming_tick_entity = FarmingTickOffsetSensor(username, farming_tick_unique_id)
    entities.append(farming_tick_entity)

    for daily_sensor in DAILY_SENSORS:
        # sanitize the daily sensor name for unique_id
        sensor_name = daily_sensor.replace("_", " ").lower()
        unique_id = f"runelite_{usernameFixed.lower()}_daily_{daily_sensor}"
        _LOGGER.debug('Setting up daily sensor for %s: %s', usernameFixed, unique_id)

        entity = DailySensor(username, sensor_name, unique_id)
        entities.append(entity)

    async_add_entities(entities)

    _LOGGER.debug('Added %d sensors for %s', len(entities), username)

    if "entities" not in hass.data[DOMAIN][config_entry.entry_id]:
        hass.data[DOMAIN][config_entry.entry_id]["entities"] = {}
    for entity in entities:
        hass.data[DOMAIN][config_entry.entry_id]["entities"][entity.entity_id] = entity
