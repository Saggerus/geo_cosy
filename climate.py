import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from .const import DOMAIN
import asyncio

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Cosy Climate platform from a config entry."""
    _LOGGER.debug("Setting up Cosy Climate entities")

    # Retrieve the API instance directly from hass.data
    api = hass.data[DOMAIN][entry.entry_id]

    # Ensure the session is properly initialized before making any API calls
    async with api:
        _LOGGER.debug("Inside async with block: _LOGGER is accessible")
        # Test API connection

        try:
            _LOGGER.debug("Attempting to log in to the API")
            # Log in to retrieve the token and system ID
            await api.login()  # Ensure we're logged in
            _LOGGER.debug("Successfully logged in to the API")

            system_id = await api.get_system_id()
            _LOGGER.debug("System ID fetched: %s", system_id)

            if not system_id:
                _LOGGER.debug("system_id test")
                _LOGGER.error("Cosy system ID is unavailable during setup")
                return

            try:
                _LOGGER.debug("Attempting to fetch the current temperature")
                temperature = await api.get_current_temperature()
                _LOGGER.debug("Current temperature fetched successfully: %s", temperature)
            except Exception as temp_error:
                _LOGGER.error("Error fetching current temperature: %s", temp_error)
                return

            if temperature is None:
                _LOGGER.debug("temperature test")
                _LOGGER.error("Failed to fetch temperature data from Cosy API")
                return
        except Exception as e:
            _LOGGER.debug("exception test")
            _LOGGER.error("Error setting up Cosy Climate: %s", e)
            return

        # Create and add the CosyClimate entity
        async_add_entities([CosyClimate(api, system_id)])


class CosyClimate(ClimateEntity):
    """Representation of a Cosy climate device."""

    def __init__(self, api, system_id):
        """Initialize the climate entity."""
        self.api = api
        self.system_id = system_id
        self._attr_name = "Cosy Thermostat"
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_current_temperature = None
        self._attr_target_temperature = None
        self._attr_unique_id = None  # Start with None

    async def async_added_to_hass(self):
        """When entity is added to Home Assistant."""
        if not self.api.system_id:
            await self.api.get_system_id()
        self._attr_unique_id = self.api.unique_id  # Set the unique_id after system_id is fetched

    async def async_update(self):
        """Fetch the latest data from the API."""
        try:
            # Ensure the session is logged in and fetch data
            await self.api.login()  # Log in to ensure we have a token
            temperature = await self.api.get_current_temperature()

            if temperature is not None:
                self._attr_current_temperature = temperature
            else:
                _LOGGER.warning("Failed to retrieve current temperature data.")
                self._attr_current_temperature = 0  # Fallback value if temperature isn't available

            # Fetch target temperature (if necessary)
            target_temp = await self.api.get_target_temperature("cosy")
            if target_temp is not None:
                self._attr_target_temperature = target_temp
        except Exception as e:
            _LOGGER.error("Error updating Cosy Climate entity: %s", e)

    async def async_set_temperature(self, **kwargs):
        """Set the target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            temperature = kwargs[ATTR_TEMPERATURE]
            try:
                await self.api.set_target_temperature(temperature)
                self._attr_target_temperature = temperature
                _LOGGER.debug("Set target temperature to %s", temperature)
            except Exception as e:
                _LOGGER.error("Error setting temperature via Cosy API: %s", e)
