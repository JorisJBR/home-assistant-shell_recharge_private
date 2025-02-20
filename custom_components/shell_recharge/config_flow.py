"""Config flow for shell_recharge integration."""
from __future__ import annotations

from asyncio import CancelledError
from typing import Any

import shellrecharge
import voluptuous as vol
from aiohttp.client_exceptions import ClientError
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from shellrecharge import LocationEmptyError, LocationValidationError

from .const import DOMAIN

RECHARGE_SCHEMA = vol.Schema({
    vol.Required("email"): str,
    vol.Required("password"): str,
})

class ShellRechargeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[misc, call-arg]
    """Handle a config flow for shell_recharge_ev."""

    VERSION = 2

    def __init__(self):
        self.user = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=RECHARGE_SCHEMA)

        try:
            api = shellrecharge.Api(websession=async_get_clientsession(self.hass))
            self.user = await api.get_user(user_input["email"], user_input["password"])
            await self.user.authenticate()
        except (ClientError, TimeoutError, CancelledError):
            errors["base"] = "cannot_connect"
        except Exception as e:
            errors["base"] = "unknown_error"
            _LOGGER.error("Unexpected exception: %s", e)

        if not errors:
            return await self.async_step_select_card()

        return self.async_show_form(
            step_id="user", data_schema=RECHARGE_SCHEMA, errors=errors
        )

    async def async_step_select_card(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the step of selecting a card."""
        errors: dict[str, str] = {}
        if user_input is None:
            card_options = await self.get_card_options()
            return self.async_show_form(
                step_id="select_card", data_schema=vol.Schema({
                    vol.Required("card_rfid"): vol.In(card_options)
                })
            )

        return await self.async_step_select_charger(user_input)

    async def async_step_select_charger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the step of selecting a charger."""
        errors: dict[str, str] = {}
        if user_input is None:
            charger_options = await self.get_charger_options()
            return self.async_show_form(
                step_id="select_charger", data_schema=vol.Schema({
                    vol.Required("charger_id"): vol.In(charger_options)
                })
            )

        user_input.update(self.user_input)
        await self.async_set_unique_id(user_input["charger_id"])
        self._abort_if_unique_id_configured(updates=user_input)
        return self.async_create_entry(
            title=f"Shell Recharge Charger {user_input['charger_id']}",
            data=user_input,
        )

    async def get_card_options(self) -> list:
        """Get the list of card options."""
        card_options = []
        async for card in self.user.get_cards():
            card_options.append(card.rfid)
        return card_options

    async def get_charger_options(self) -> list:
        """Get the list of charger options."""
        chargers = await self.user.get_chargers()
        return [charger.id for charger in chargers]
