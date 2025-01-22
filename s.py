from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Geo Cosy sensors based on a config entry."""
    # Retrieve the API instance from hass.data
    api = hass.data[DOMAIN][config_entry.entry_id]

    # Create sensors
    sensors = [
        CosyTemperatureSensor(api),
        CosyPresetModeSensor(api),
    ]
    async_add_entities(sensors, update_before_add=True)


class CosyTemperatureSensor(SensorEntity):
    """Representation of a Geo Cosy temperature sensor."""

    def __init__(self, api):
        """Initialize the temperature sensor."""
        self.api = api
        self._attr_name = "Cosy Temperature"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_unique_id = "geo_cosy_temperature"
        self._state = None

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            self._state = await self.api.get_current_temperature()
        except Exception as e:
            self._state = None

    @property
    def native_value(self):
        """Return the current temperature."""
        return self._state


class CosyPresetModeSensor(SensorEntity):
    """Representation of a Geo Cosy preset mode sensor."""

    def __init__(self, api):
        """Initialize the preset mode sensor."""
        self.api = api
        self._attr_name = "Cosy Preset Mode"
        self._attr_unique_id = "geo_cosy_preset_mode"
        self._state = None

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            self._state = await self.api.get_current_preset()
        except Exception as e:
            self._state = None

    @property
    def native_value(self):
        """Return the current preset mode."""
        return self._state
