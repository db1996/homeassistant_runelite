"""Services for the RuneLite Farming integration."""

import logging
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import config_validation as cv
from .sensor import FarmingPatchTypeSensor, FarmingContractSensor, FarmingTickOffsetSensor, BirdhousesSensor  # Import your sensor class if needed
from datetime import datetime, timedelta, timezone
from .const import DOMAIN, PATCH_TYPE_DATA, CROP_TYPE_DATA  # Import constants
from .patch_calculator import PatchCalculator  # Import your calculator function

import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

AVAILABLE_PATCH_TYPES = list(PATCH_TYPE_DATA.keys())
AVAILABLE_CROP_TYPES = list(CROP_TYPE_DATA.keys())

# Define the input schema for the set_patch_completion service
SET_ENTITY_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("completion_time"): cv.datetime,
        vol.Optional("status"): cv.string,
        vol.Optional("crop_type"): cv.string,
        vol.Optional("patch_type"): cv.string,
    }
)

SET_MULTI_ENTITY_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("entities"): vol.All(
            [  # A list of dicts with the same schema as SET_ENTITY_DATA_SCHEMA
                vol.Schema(
                    {
                        vol.Required("entity_id"): cv.entity_id,
                        vol.Optional("completion_time"): cv.datetime,
                        vol.Optional("status"): cv.string,
                        vol.Optional("crop_type"): cv.string,
                        vol.Optional("patch_type"): cv.string,
                    }
                )
            ]
        )
    }
)

CALCULATE_FARMING_CONTRACT_SCHEMA = vol.Schema(
    {
        vol.Optional("username"): cv.string,
        vol.Optional("patch_type"): vol.In(AVAILABLE_PATCH_TYPES),
        vol.Optional("crop_type"): vol.In(AVAILABLE_CROP_TYPES),
    }
)

# Define the input schema for the calculate_completion_time service with options
CALCULATE_PATCH_OR_CROP_SCHEMA = vol.Schema(
    {
        vol.Optional("username"): cv.string,
        vol.Optional("patch_type"): vol.In(AVAILABLE_PATCH_TYPES),
        vol.Optional("crop_type"): vol.In(AVAILABLE_CROP_TYPES),
    }
)

# Define the input schema for the set_farming_tick_offset service
SET_FARMING_TICK_OFFSET_SCHEMA = vol.Schema(
    {
        vol.Optional("username"): cv.string,
        vol.Optional("farming_tick_offset"): vol.All(int, vol.Range(min=-30, max=30)),
    }
)

SET_PATCH_DIRECTLY_SCHEMA = vol.Schema(
    {
        vol.Optional("username"): cv.string
    }
)

SET_PATCH_WITH_CROP_SCHEMA = vol.Schema(
    {
        vol.Optional("username"): cv.string,
        vol.Optional("crop_type"): vol.In(AVAILABLE_CROP_TYPES),
    }
)


class RuneLiteFarmingServices:
    """Class to handle RuneLite Farming Services."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize services."""
        self.hass = hass
        self.config_entry = config_entry
        self.farming_tick_offset = 0
        username = self.get_default_username()
        self.calculator = PatchCalculator(self.hass, username)
        self.setup_services()

    def setup_services(self):
        """Register the services in Home Assistant."""
        self.hass.services.async_register(
            DOMAIN, 
            "set_multi_entity_data", 
            self.async_set_multi_entity_data_service,
            schema=SET_MULTI_ENTITY_DATA_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "set_entity_data", 
            self.async_set_entity_data_service,
            schema=SET_ENTITY_DATA_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "calculate_patch_or_crop", 
            self.async_calculate_patch_or_crop_service,
            schema=CALCULATE_PATCH_OR_CROP_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "calculate_farming_contract", 
            self.async_calculate_farming_contract_service,
            schema=CALCULATE_PATCH_OR_CROP_SCHEMA,
        )

        self.hass.services.async_register(
            DOMAIN, 
            "set_farming_tick_offset", 
            self.async_set_farming_tick_offset_service,
            schema=SET_FARMING_TICK_OFFSET_SCHEMA,
        )

        self.hass.services.async_register(
            DOMAIN, 
            "reset_birdhouses", 
            self.async_reset_birdhouses_services,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )

        # Directly set patch types
        self.hass.services.async_register(
            DOMAIN, 
            "herb_patch", 
            self.async_herb_patch_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "tree_patch", 
            self.async_tree_patch_service,
            schema=SET_PATCH_WITH_CROP_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "fruit_tree_patch", 
            self.async_fruit_tree_patch_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "bush_patch", 
            self.async_bush_patch_service,
            schema=SET_PATCH_WITH_CROP_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "hespori_patch", 
            self.async_hespori_patch_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "hardwood_patch", 
            self.async_hardwood_patch_service,
            schema=SET_PATCH_WITH_CROP_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "allotment_patch", 
            self.async_allotment_patch_service,
            schema=SET_PATCH_WITH_CROP_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "flower_patch", 
            self.async_flower_patch_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "cactus_patch", 
            self.async_cactus_patch_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "potato_cactus_patch", 
            self.async_potato_cactus_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "mushroom_patch", 
            self.async_mushroom_patch_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "spirit_tree_patch", 
            self.async_spirit_tree_patch_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN,
            "redwood_patch",
            self.async_redwood_patch_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )

        # Set Farming contract directly to patches
        self.hass.services.async_register(
            DOMAIN, 
            "farming_contract_allotment", 
            self.async_farming_contract_allotment_service,
            schema=SET_PATCH_WITH_CROP_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "farming_contract_bush", 
            self.async_farming_contract_bush_service,
            schema=SET_PATCH_WITH_CROP_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "farming_contract_cactus", 
            self.async_farming_contract_cactus_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "farming_contract_potato_cactus", 
            self.async_farming_contract_potato_cactus_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "farming_contract_flower", 
            self.async_farming_contract_flower_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "farming_contract_fruit_tree", 
            self.async_farming_contract_fruit_tree_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "farming_contract_herb", 
            self.async_farming_contract_herb_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "farming_contract_tree", 
            self.async_farming_contract_tree_service,
            schema=SET_PATCH_WITH_CROP_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN, 
            "farming_contract_redwood", 
            self.async_farming_contract_redwood_service,
            schema=SET_PATCH_DIRECTLY_SCHEMA,
        )

    def get_default_username(self) -> str:
        """Get the default username from the config entry."""
        return self.config_entry.data.get("username", "").replace(" ", "_").lower()
    
    async def async_update_entity_data(self, entity_id: str, data: dict) -> None:
        """Set data for a specific entity."""
        integration_data = self.hass.data.get(DOMAIN, {})
        for entry_id, entry_data in integration_data.items():
            sensor_entity = entry_data.get("entities", {}).get(entity_id)
            _LOGGER.info(f"trying to find entity '{entity_id}' with data: {data}")
            _LOGGER.info(f"sensor_entity: {sensor_entity}")
            # log the instance type
            _LOGGER.info(f"sensor_entity type: {type(sensor_entity)}")
            if isinstance(sensor_entity, (FarmingPatchTypeSensor, FarmingContractSensor, FarmingTickOffsetSensor, BirdhousesSensor)):
                _LOGGER.info(f"Updating entity '{entity_id}' with data: {data}")
                await sensor_entity.update_data(data)
                return
        _LOGGER.warning(f"Entity '{entity_id}' not found in the integration data.")

    async def async_set_multi_entity_data_service(self, service: ServiceCall) -> None:
        """Set data for multiple farming patch entities in one call."""
        entities_data = service.data.get("entities", [])
        _LOGGER.info(f"Setting data for multiple entities: {entities_data}")
        
        for entity_data in entities_data:
            entity_id = entity_data.get("entity_id")
            if not entity_id:
                _LOGGER.error("Entity ID is required.", )
                continue  # Optionally raise/log error here

            update_data = {}
            if "completion_time" in entity_data:
                update_data["completion_time"] = entity_data["completion_time"]
            if "status" in entity_data:
                update_data["status"] = entity_data["status"]
            if "crop_type" in entity_data:
                update_data["crop_type"] = entity_data["crop_type"]
            if "patch_type" in entity_data:
                update_data["patch_type"] = entity_data["patch_type"]

            await self.async_update_entity_data(entity_id, update_data)
        return

    async def async_set_entity_data_service(self, service: ServiceCall) -> None:
        """Set the completion time and/or status of a farming patch."""
        entity_id = service.data.get("entity_id")
        completion_time = service.data.get("completion_time")
        status = service.data.get("status")
        crop_type = service.data.get("crop_type")
        patch_type = service.data.get("patch_type")
        
        update_data = {}
        if completion_time:
            update_data["completion_time"] = completion_time
        if status:
            update_data["status"] = status
        if crop_type:
            update_data["crop_type"] = crop_type
        if patch_type:
            update_data["patch_type"] = patch_type

        await self.async_update_entity_data(entity_id, update_data)
        return
    
    async def async_calculate_patch_or_crop_service(self, service: ServiceCall) -> None:
        """Calculate and log the crop completion time."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()
        entity_id = f"sensor.runelite_{username}_{patch_type}_patch"
        crop_type = service.data.get("crop_type")
        patch_type = service.data.get("patch_type")
        update_data = self.calculator.calculate(crop_type, patch_type, "in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_calculate_farming_contract_service(self, service: ServiceCall) -> None:
        """Set the farming contract to a patch/crop, calculate automatically."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        crop_type = service.data.get("crop_type")
        patch_type = service.data.get("patch_type")
        update_data = self.calculator.calculate(crop_type, patch_type, "in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_set_farming_tick_offset_service(self, service: ServiceCall) -> None:
        """Set the farming tick offset for the user."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()
        entity_id = f"sensor.runelite_{username}_farming_tick_offset"
        _LOGGER.info(f"Setting farming tick offset for '{username}' to." )
        _LOGGER.info(f"Service data: {service.data}")
        update_data = {
            "farming_tick_offset": service.data.get("farming_tick_offset")
        }
        await self.async_update_entity_data(entity_id, update_data)

    async def async_reset_birdhouses_services(self, service: ServiceCall) -> None:
        """Reset the birdhouses."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_birdhouses"
        completion_time = datetime.now(timezone.utc) + timedelta(minutes=50)
        update_data = {
            "completion_time": completion_time,
            "status": "in_progress",
        }
        await self.async_update_entity_data(entity_id, update_data)

    # Directly set patch types
    ## These functions are used to set the patch types directly.
    async def async_herb_patch_service(self, service: ServiceCall) -> None:
        """Set the herb patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()
        entity_id = f"sensor.runelite_{username}_herb_patch"
        update_data = self.calculator.calculate(patch_type="herb", status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_tree_patch_service(self, service: ServiceCall) -> None:
        """Set the tree patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()
        
        tree_patch = service.data.get("crop_type")

        entity_id = f"sensor.runelite_{username}_tree_patch"
        update_data = self.calculator.calculate(patch_type="tree", crop_type=tree_patch, status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_fruit_tree_patch_service(self, service: ServiceCall) -> None:
        """Set the fruit tree patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()
        

        entity_id = f"sensor.runelite_{username}_fruit_tree_patch"
        update_data = self.calculator.calculate(patch_type="fruit_tree", status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_bush_patch_service(self, service: ServiceCall) -> None:
        """Set the nush patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()
        
        bush_patch = service.data.get("crop_type")

        entity_id = f"sensor.runelite_{username}_bush_patch"
        update_data = self.calculator.calculate(patch_type="bush", crop_type=bush_patch, status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_hespori_patch_service(self, service: ServiceCall) -> None:
        """Set the hespori patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()
        
        entity_id = f"sensor.runelite_{username}_hespori_patch"
        update_data = self.calculator.calculate(patch_type="hespori", status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_hardwood_patch_service(self, service: ServiceCall) -> None:
        """Set the hardwood patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        hardwood_patch = service.data.get("crop_type")
        
        entity_id = f"sensor.runelite_{username}_hardwood_patch"
        update_data = self.calculator.calculate(patch_type="hardwood", crop_type=hardwood_patch, status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_allotment_patch_service(self, service: ServiceCall) -> None:
        """Set the allotment patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        allotment_patch = service.data.get("crop_type")
        
        entity_id = f"sensor.runelite_{username}_allotment_patch"
        update_data = self.calculator.calculate(patch_type="allotment", crop_type=allotment_patch, status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_flower_patch_service(self, service: ServiceCall) -> None:
        """Set the flower patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_flower_patch"
        update_data = self.calculator.calculate(patch_type="flower", status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_cactus_patch_service(self, service: ServiceCall) -> None:
        """Set the cactus patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_cactus_patch"
        update_data = self.calculator.calculate(patch_type="cactus", status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_potato_cactus_service(self, service: ServiceCall) -> None:
        """Set the potato cactus patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_potato_cactus_patch"
        update_data = self.calculator.calculate(patch_type="potato_cactus", status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_mushroom_patch_service(self, service: ServiceCall) -> None:
        """Set the mushroom patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_mushroom_patch"
        update_data = self.calculator.calculate(patch_type="mushroom", status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_spirit_tree_patch_service(self, service: ServiceCall) -> None:
        """Set the spirit tree patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_spirit_tree_patch"
        update_data = self.calculator.calculate(patch_type="spirit_tree", status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
        
    async def async_redwood_patch_service(self, service: ServiceCall) -> None:
        """Set the redwood patch directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_redwood_patch"
        update_data = self.calculator.calculate(patch_type="redwood", status="in_progress")
        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    ## Set Farming contract directly to patches
    async def async_farming_contract_allotment_service(self, service: ServiceCall) -> None:
        """Set the farming contract directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        allotment_patch = service.data.get("crop_type")
        update_data = self.calculator.calculate(patch_type="allotment", crop_type=allotment_patch, status="in_progress")

        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_farming_contract_bush_service(self, service: ServiceCall) -> None:
        """Set the farming contract directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        bush_patch = service.data.get("crop_type")
        update_data = self.calculator.calculate(patch_type="bush", crop_type=bush_patch, status="in_progress")

        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_farming_contract_cactus_service(self, service: ServiceCall) -> None:
        """Set the farming contract directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        update_data = self.calculator.calculate(patch_type="cactus", status="in_progress")

        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_farming_contract_potato_cactus_service(self, service: ServiceCall) -> None:
        """Set the farming contract directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        update_data = self.calculator.calculate(patch_type="potato_cactus", status="in_progress")

        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_farming_contract_flower_service(self, service: ServiceCall) -> None:
        """Set the farming contract directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        flower_patch = service.data.get("crop_type")
        update_data = self.calculator.calculate(patch_type="flower", crop_type=flower_patch, status="in_progress")

        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    
    async def async_farming_contract_fruit_tree_service(self, service: ServiceCall) -> None:
        """Set the farming contract directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        update_data = self.calculator.calculate(patch_type="fruit_tree", status="in_progress")

        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)
    async def async_farming_contract_herb_service(self, service: ServiceCall) -> None:
        """Set the farming contract directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        update_data = self.calculator.calculate(patch_type="herb", status="in_progress")

        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_farming_contract_tree_service(self, service: ServiceCall) -> None:
        """Set the farming contract directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        tree_patch = service.data.get("crop_type")
        update_data = self.calculator.calculate(patch_type="tree", crop_type=tree_patch, status="in_progress")

        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

    async def async_farming_contract_redwood_service(self, service: ServiceCall) -> None:
        """Set the farming contract directly."""
        username = None
        if service.data.get("username"): 
            username = service.data.get("username").replace(" ", "_").lower()
        else:
            username = self.get_default_username()

        entity_id = f"sensor.runelite_{username}_farming_contract"
        update_data = self.calculator.calculate(patch_type="redwood", status="in_progress")

        if(update_data == None):
            _LOGGER.warning("Could not calculate farming contract.")
            return
        await self.async_update_entity_data(entity_id, update_data)

@callback
def async_register_services(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Register the RuneLite Farming services."""
    RuneLiteFarmingServices(hass, config_entry)