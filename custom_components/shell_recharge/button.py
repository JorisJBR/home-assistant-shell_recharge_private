from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import Entity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the button entities."""
    client = hass.data[DOMAIN]["client"]
    async_add_entities([ShellRechargeStartButton(client), ShellRechargeStopButton(client)])

class ShellRechargeStartButton(ButtonEntity):
    """Button to start charging session."""

    def __init__(self, client):
        self._client = client
        self._attr_name = "Start Charging"

    async def async_press(self):
        """Handle button press."""
        await self._client.start_charging()

class ShellRechargeStopButton(ButtonEntity):
    """Button to stop charging session."""

    def __init__(self, client):
        self._client = client
        self._attr_name = "Stop Charging"

    async def async_press(self):
        """Handle button press."""
        await self._client.stop_charging()
