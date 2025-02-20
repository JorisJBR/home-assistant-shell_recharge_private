"""Platform for Shell Recharge switch integration."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Shell Recharge switch based on a config entry."""
    email = config_entry.data["email"]
    password = config_entry.data["password"]
    charger_id = config_entry.data["charger_id"]
    card_rfid = config_entry.data["card_rfid"]
    
    session = async_get_clientsession(hass)
    api = shellrecharge.Api(session)
    user = await api.get_user(email, password)
    await user.authenticate()
    
    async_add_entities([ShellRechargeSwitch(user, charger_id, card_rfid)])


class ShellRechargeSwitch(SwitchEntity):
    """Representation of a Shell Recharge switch."""

    def __init__(self, user, charger_id, card_rfid):
        """Initialize the switch."""
        self.user = user
        self.charger_id = charger_id
        self.card_rfid = card_rfid
        self._is_on = False

    @property
    def name(self):
        """Return the name of the switch."""
        return f"Shell Recharge Charger {self.charger_id}"

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        try:
            await self.user.toggle_charger(self.charger_id, self.card_rfid, True)
            self._is_on = True
            self.async_schedule_update_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to turn on the charger: %s", e)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        try:
            await self.user.toggle_charger(self.charger_id, self.card_rfid, False)
            self._is_on = False
            self.async_schedule_update_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to turn off the charger: %s", e)
