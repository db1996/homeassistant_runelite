"""Sensor platform for RuneLite Farming integration."""

from __future__ import annotations

import logging

from custom_components.runelite.sensors.player_health import PlayerHealth
from custom_components.runelite.sensors.player_prayer import PlayerPrayer
from custom_components.runelite.sensors.player_run_energy import PlayerRunEnergy
from custom_components.runelite.sensors.player_special_attack import PlayerSpecialAttack
from custom_components.runelite.sensors.player_status_effects import PlayerStatusEffects
from custom_components.runelite.sensors.player_status import PlayerStatus
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
from .sensors.aggression import AgressionSensor
from .helpers import sanitize

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

    max_health = 0
    max_prayer = 0
    if coordinator.data:
        for skill in coordinator.data.get("skills", []):
            skill_name = skill.get('name').lower()
            if skill_name in ["overall"]:
                skill_name = "total"  # Normalize the name for the total skill

            if skill_name == "hitpoints":
                max_health = skill.get('Level', 0)

            elif skill_name == "prayer":
                max_prayer = skill.get('Level', 0)


            skill['name'] = skill_name.capitalize()  # Capitalize the skill name for display
                
            skill_entity = OsrsSkillSensor(
                coordinator,
                username,
                skill
            )
            entities.append(skill_entity)
        for activity in coordinator.data.get("activities", []):
            activity_name = activity.get('name').lower()
            activity['name'] = activity_name.capitalize()  # Capitalize the activity name for display
            activity_entity = OsrsActivitySensor(
                coordinator,
                username,
                activity
            )
            _LOGGER.debug('Adding activity sensor for %s: %s', username, activity_name)
            entities.append(activity_entity)

    usernameFixed = username.replace(" ", "_").lower()
    _LOGGER.debug('Setting up sensors for %s', username)
    for patch_type, patch_data in PATCH_TYPE_DATA.items():
        # sanitize the patch type for unique_id
        _LOGGER.debug('Setting up sensors for %s %s', usernameFixed, patch_type)

        entity = FarmingPatchTypeSensor(username, patch_type, patch_data)
        entities.append(entity)

    # Add a generic contract sensor for this username (keeping this for now)
    contract_entity = FarmingContractSensor(username)
    entities.append(contract_entity)

    birdhouse_entity = BirdhousesSensor(username)
    entities.append(birdhouse_entity)

    big_compost_entity = CompostBinSensor(username)
    entities.append(big_compost_entity)

    farming_tick_entity = FarmingTickOffsetSensor(username)
    entities.append(farming_tick_entity)

    for daily_sensor in DAILY_SENSORS:
        # sanitize the daily sensor name for unique_id
        sensor_name = sanitize(daily_sensor)
        _LOGGER.debug('Setting up daily sensor for %s: %s', usernameFixed, sensor_name)

        entity = DailySensor(username, sensor_name)
        entities.append(entity)
    _LOGGER.warning("Creating player stats", max_health, max_prayer)
    health_entity = PlayerHealth(username, max_health)
    entities.append(health_entity)

    prayer_entity = PlayerPrayer(username, max_prayer)
    entities.append(prayer_entity)

    run_energy_entity = PlayerRunEnergy(username)
    entities.append(run_energy_entity)

    special_attack_entity = PlayerSpecialAttack(username)
    entities.append(special_attack_entity)

    status_effects_entity = PlayerStatusEffects(username)
    entities.append(status_effects_entity)

    player_status_entity = PlayerStatus(username)
    entities.append(player_status_entity)

    aggression_entity = AgressionSensor(username)
    entities.append(aggression_entity)

    async_add_entities(entities)

    _LOGGER.debug('Added %d sensors for %s', len(entities), username)

    if "entities" not in hass.data[DOMAIN][config_entry.entry_id]:
        hass.data[DOMAIN][config_entry.entry_id]["entities"] = {}
    for entity in entities:
        hass.data[DOMAIN][config_entry.entry_id]["entities"][entity.entity_id] = entity
