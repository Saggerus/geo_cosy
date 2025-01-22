from homeassistant import config_entries
from .api import CosyAPI  # Adjust the import path if necessary
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
    }
)


class GeoCosyConfigFlow(config_entries.ConfigFlow, domain="geo_cosy"):
    """Handle a config flow for Geo Cosy."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            username = user_input["username"]
            password = user_input["password"]

            try:
                # Use 'async with' to manage the CosyAPI session
                async with CosyAPI(username, password) as api:
                    await api.login()
                    if not api.token:
                        errors["base"] = "invalid_auth"
                    else:
                        # Successful login, create the config entry
                        return self.async_create_entry(title="Geo Cosy", data=user_input)
            except Exception as e:
                # Log the exception if necessary
                errors["base"] = "cannot_connect"

        # Show the configuration form with errors if any
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)