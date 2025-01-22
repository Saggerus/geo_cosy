from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .api import CosyAPI

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Geo Cosy from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create and store the API instance
    username = entry.data["username"]
    password = entry.data["password"]

    # Initialize the API instance
    api = CosyAPI(username, password)  # Ensure `hass` is passed if required
    hass.data[DOMAIN][entry.entry_id] = api

    # Forward the entry setup to the climate platform
    await hass.config_entries.async_forward_entry_setups(entry, ["climate"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove API instance
    hass.data[DOMAIN].pop(entry.entry_id, None)

    # Unload the sensor and climate platforms
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    unload_ok = unload_ok and await hass.config_entries.async_forward_entry_unload(entry, "climate")

    return unload_ok
