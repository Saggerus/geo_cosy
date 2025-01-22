import logging
import aiohttp
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from .const import DOMAIN
from .api import CosyAPI

_LOGGER = logging.getLogger(__name__)

PRESET_MODE_MAP = {
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
        self._attr_preset_modes = ["slumber", "comfy", "cosy"]
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        self._attr_current_temperature = None
        self._attr_target_temperature = None
        self._attr_unique_id = f"cosy_thermostat_{self.api.system_id}"

    async def async_added_to_hass(self):
        """When entity is added to Home Assistant."""
        await self.async_update()

    async def async_update(self):
        """Fetch the latest data from the API."""
        try:
            await self.api.login()
            self._attr_current_temperature = await self.api.get_current_temperature()
            preset_mode = await self.api.get_current_preset()
            self._attr_preset_mode = PRESET_MODE_MAP.get(preset_mode, "slumber")
            self._attr_hvac_mode = HVACMode.HEAT if preset_mode != 0 else HVACMode.OFF
            self._attr_target_temperature = await self.api.get_target_temperature(self._attr_preset_mode)
        except Exception as e:
            _LOGGER.error("Error updating Cosy Climate entity: %s", e)

    async def async_set_temperature(self, **kwargs):
        """Set the target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            temperature = kwargs[ATTR_TEMPERATURE]
            try:
                await self.api.set_target_temperature(self._attr_preset_mode, temperature)
                self._attr_target_temperature = temperature
                await self.async_update_ha_state()
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
                await self.api.set_preset_mode(self._attr_preset_mode)
            self._attr_hvac_mode = hvac_mode
            self._attr_target_temperature = await self.api.get_target_temperature(self._attr_preset_mode)
            await self.async_update_ha_state()
        except aiohttp.ClientResponseError as e:
            if e.status == 405:
                _LOGGER.error("Error setting HVAC mode via Cosy API: %s, message='%s', url='%s'", e.status, e.message, e.request_info.url)
            else:
                _LOGGER.error("Error setting HVAC mode via Cosy API: %s", e)

    async def async_set_preset_mode(self, preset_mode):
        """Set the preset mode."""
        try:
            if await self.api.get_current_preset() == 0:
                await self.api.set_hibernate_mode(False)
            await self.api.set_preset_mode(preset_mode)
            self._attr_preset_mode = preset_mode
            self._attr_hvac_mode = HVAC_MODE_MAP.get(preset_mode, HVACMode.HEAT)
            self._attr_target_temperature = await self.api.get_target_temperature(preset_mode)
            await self.async_update_ha_state()
        except aiohttp.ClientResponseError as e:
            if e.status == 405:
                _LOGGER.error("Error setting preset mode via Cosy API: %s, message='%s', url='%s'", e.status, e.message, e.request_info.url)
            else:
                _LOGGER.error("Error setting preset mode via Cosy API: %s", e)

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._attr_target_temperature

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._attr_current_temperature

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return 5.0

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return 30.0

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._attr_temperature_unit

    @property
    def hvac_mode(self):
        """Return current operation mode."""
        return self._attr_hvac_mode

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._attr_hvac_modes

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        return self._attr_preset_mode

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return self._attr_preset_modes

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._attr_supported_features

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:thermostat"