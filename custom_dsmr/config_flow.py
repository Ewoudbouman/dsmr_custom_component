"""Config flow for custom dsmr integration."""
import asyncio
import logging
from urllib.parse import urlparse

import async_timeout
import voluptuous as vol
from aiohttp import ClientError

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_HISTORY_DAY,  # pylint:disable=unused-import
    CONF_HISTORY_HOUR,
    CONF_HISTORY_MONTH,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


INPUT_SCHEMA = {
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_HISTORY_HOUR, default=False): cv.boolean,
    vol.Optional(CONF_HISTORY_DAY, default=False): cv.boolean,
    vol.Optional(CONF_HISTORY_MONTH, default=False): cv.boolean,
}


class DSMRSetup:
    """Test if the configuration to setup the dsmr connection is valid."""

    def __init__(self, host, hass):
        """Initialize the dsmr connection setup."""
        self._host = host
        self._session = async_get_clientsession(hass)  # session

    async def check_host(self) -> bool:
        """Test if we can authenticate with the host."""
        dmsr_api_reply = self._host + "/api/v1/dev/info"

        try:
            with async_timeout.timeout(10):
                await self._session.get(dmsr_api_reply)
        except (asyncio.TimeoutError, ClientError):
            return False

        return True


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input required to setup the connection."""
    dsmr_setup = DSMRSetup(data["host"], hass)
    if not await dsmr_setup.check_host():
        raise CannotConnect
    return {"title": "custom_dsmr"}


def parse_host(host):
    """Format the url string into http://url."""
    return "http://" + urlparse(host).netloc


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for custom dsmr."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                user_input["host"] = parse_host(user_input["host"])
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(INPUT_SCHEMA),
            errors=errors,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
