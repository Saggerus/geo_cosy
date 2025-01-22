import logging
import aiohttp
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from .const import DOMAIN
from .api import CosyAPI

_LOGGER = logging.getLogger(__name__)

PRESET_MODE_MAP = {
    0: "hibernate",
    1: "slumber",
    2: "comfy",
    3: "cosy",
}

HVAC_MODE_MAP = {
    "hibernate": HVACMode.OFF,
    "slumber": HVACMode.HEAT,
    "comfy": HVACMode.HEAT,
    "cosy": HVACMode.HEAT,
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Cosy Climate platform from a config entry."""
    _LOGGER.debug("Setting up Cosy Climate entities")

    api = CosyAPI(entry.data["username"], entry.data["password"])
    await api.login()
    await api.get_system_id()

    async_add_entities([CosyClimate(api)])


class CosyClimate(ClimateEntity):
    """Representation of a Cosy climate device."""

    def __init__(self, api):
        """Initialize the climate entity."""
        self.api = api
        self._attr_name = "Cosy Thermostat"
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self._attr_preset_mode = "cosy"
        self._attr_preset_modes = ["hibernate", "slumber", "comfy", "cosy"]
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        self._attr_current_temperature = None
        self._attr_target_temperature = None
        self._attr_unique_id = f"cosy_thermostat_{self.api.system_id}"

    async def async_added_to_hass(self):
        """When entity is added to Home Assistant."""
        _LOGGER.debug("Entity added to Home Assistant")
        await self.async_update()

    async def async_update(self):
        """Fetch the latest data from the API."""
        try:
            await self.api.login()
            self._attr_current_temperature = await self.api.get_current_temperature()
            preset_mode = await self.api.get_current_preset()
            self._attr_preset_mode = PRESET_MODE_MAP.get(preset_mode, "hibernate")
            self._attr_hvac_mode = HVAC_MODE_MAP.get(self._attr_preset_mode, HVACMode.OFF)
            _LOGGER.debug("Updated current temperature: %s", self._attr_current_temperature)
            _LOGGER.debug("Updated current preset mode: %s", self._attr_preset_mode)
        except Exception as e:
            _LOGGER.error("Error updating Cosy Climate entity: %s", e)

    async def async_set_temperature(self, **kwargs):
        """Set the target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            temperature = kwargs[ATTR_TEMPERATURE]
            try:
                await self.api.set_target_temperature(self._attr_preset_mode, temperature)
                self._attr_target_temperature = temperature
                _LOGGER.debug("Set target temperature to %s", temperature)
            except Exception as e:
                _LOGGER.error("Error setting temperature via Cosy API: %s", e)

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the HVAC mode."""
        try:
            if hvac_mode == HVACMode.OFF:
                await self.api.set_hibernate_mode(True)
            else:
                if await self.api.get_current_preset() == 0:
                    await self.api.set_hibernate_mode(False)
                await self.api.set_preset_mode(hvac_mode)
            self._attr_hvac_mode = hvac_mode
            _LOGGER.debug("Set HVAC mode to %s", hvac_mode)
        except aiohttp.ClientResponseError as e:
            if e.status == 405:
                _LOGGER.error("Error setting HVAC mode via Cosy API: %s, message='%s', url='%s'", e.status, e.message, e.request_info.url)
            else:
                _LOGGER.error("Error setting HVAC mode via Cosy API: %s", e)

    async def async_set_preset_mode(self, preset_mode):
        """Set the preset mode."""
        try:
            if preset_mode == "hibernate":
                await self.api.set_hibernate_mode(True)
            else:
                if await self.api.get_current_preset() == 0:
                    await self.api.set_hibernate_mode(False)
                await self.api.set_preset_mode(preset_mode)
            self._attr_preset_mode = preset_mode
            self._attr_hvac_mode = HVAC_MODE_MAP.get(preset_mode, HVACMode.OFF)
            _LOGGER.debug("Set preset mode to %s", preset_mode)
        except aiohttp.ClientResponseError as e:
            if e.status == 405:
                _LOGGER.error("Error setting preset mode via Cosy API: %s, message='%s', url='%s'", e.status, e.message, e.request_info.url)
            else:
                _LOGGER.error("Error setting preset mode via Cosy API: %s", e)