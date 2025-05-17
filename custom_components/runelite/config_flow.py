"""Config flow for the RuneLite Farming integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required("username", "Test"): str,
        vol.Optional("farming_tick_offset"): int
    }
)


class RuneliteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for RuneLite Farming."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input["username"]
            farming_tick_offset = user_input.get("farming_tick_offset")
            await self.async_set_unique_id(f"runelite_farming_{username}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=username, data={"username": username, "farming_tick_offset": farming_tick_offset})

        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )

    async def async_step_import(
        self, import_config: dict[str, Any]
    ) -> ConfigFlowResult:
        """Import a config entry from configuration.yaml."""
        username = import_config.get("username")
        farming_tick_offset = import_config.get("farming_tick_offset")
        if username:
            await self.async_set_unique_id(f"runelite_farming_{username}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=username, data={"username": username, "farming_tick_offset": farming_tick_offset})
        return self.async_abort(reason="invalid_import")

    async def async_step_add_more(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle adding more usernames."""
        _LOGGER.debug("ConfigFlow.async_step_add_more called")
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input["username"]
            farming_tick_offset = user_input.get("farming_tick_offset")
            await self.async_set_unique_id(f"runelite_farming_{username}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=username, data={"username": username, "farming_tick_offset": farming_tick_offset})

        return self.async_show_form(
            step_id="add_more", data_schema=USER_SCHEMA, errors=errors
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step when adding a new config entry."""
        return await self.async_step_user()

    # In RuneliteConfigFlow
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Initiate options flow instance."""
        return RuneliteConfigFlow()


class ConfigFlow(config_entries.OptionsFlow):
    """Options flow handler for RuneLite Farming."""

    # In ConfigFlow
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _LOGGER.debug("ConfigFlow.async_step_init called")
        result = await self.async_step_add_username()
        _LOGGER.debug(f"async_step_add_username returned: {result}")
        return result

    async def async_step_add_username(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle adding a new username."""
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input["username"]
            farming_tick_offset = user_input.get("farming_tick_offset")
            if farming_tick_offset is None:
                farming_tick_offset = 0

            current_entries = self.hass.config_entries.async_entries(DOMAIN)
            for entry in current_entries:
                if entry.data.get("username") == username:
                    return self.async_abort(reason="username_exists")

            new_data = {"username": username, "farming_tick_offset": farming_tick_offset}
            return self.async_create_entry(title=username, data=new_data)

        # Pre-fill the form with existing options if available
        current_username = self.config_entry.data.get("username")
        current_offset = self.config_entry.data.get("farming_tick_offset", 0)
        _LOGGER.debug(f"Current username: {current_username}, Current offset: {current_offset}")
        return self.async_show_form(
            step_id="add_username",
            data_schema=vol.Schema(
                {
                    vol.Required("username", default=current_username): str,
                    vol.Optional("farming_tick_offset", default=current_offset): int,
                }
            ),
            errors=errors,
        )