import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .api import CosyAPI
import logging

_LOGGER = logging.getLogger(__name__)

class GeoCosyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Geo Cosy."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate the input
            try:
                _LOGGER.debug("Attempting to log in with provided credentials")
                # Attempt to login with provided credentials
                api = CosyAPI(user_input["username"], user_input["password"])
                token = await api.login()
                if token:
                    _LOGGER.debug("Successfully logged in")
                    return self.async_create_entry(title="Geo Cosy", data=user_input)
                else:
                    _LOGGER.error("Failed to log in, cannot_connect")
                    errors["base"] = "cannot_connect"
            except Exception as e:
                _LOGGER.error("Exception occurred: %s", e)
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return GeoCosyOptionsFlowHandler(config_entry)


class GeoCosyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Required("username", default=self.config_entry.data.get("username")): str,
            vol.Required("password", default=self.config_entry.data.get("password")): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )