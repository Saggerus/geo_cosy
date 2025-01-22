import aiohttp
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class CosyAPI:
    """Class to interact with the Geo Cosy API."""

    def __init__(self, username, password):
        self.base_url = "https://cosy.geotogether.com/api/userapi/"
        self.username = username
        self.password = password
        self.token = None
        self.system_id = None
        self.session = None  # Session will be initialized during __aenter__()

    async def __aenter__(self):
        """Initialize the aiohttp session when entering the async context."""
        if not self.session:  # Ensure the session is created only if it doesn't exist
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the aiohttp session when exiting the async context."""
        if self.session:
            await self.session.close()
            self.session = None  # Explicitly set session to None after closing it

    async def login(self):
        """Log in to the Geo Cosy API and retrieve a token."""
        login_url = self.base_url + "account/login"

        try:
            async with self.session.post(
                login_url,
                json={"name": self.username, "emailAddress": self.username, "password": self.password},
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Login failed: {response.status} - {await response.text()}")
                data = await response.json()
                self.token = data.get("token")
                return self.token
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Error during login: {e}")

    async def get_system_id(self):
        """Retrieve the system ID for the user."""
        if not self.token:
            await self.login()

        data_url = self.base_url + "user/detail-systems?peripherals=true"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with self.session.get(data_url, headers=headers) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to get system ID: {response.status} - {await response.text()}")
                data = await response.json()
                self.system_id = data.get("systemRoles", [{}])[0].get("systemId")
                return self.system_id
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Error getting system ID: {e}")

    async def get_current_temperature(self):
        """Retrieve the current temperature."""
        if not self.token or not self.system_id:
            await self.login()
            await self.get_system_id()

        data_url = self.base_url + f"system/cosy-live-data/{self.system_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with self.session.get(data_url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                if "temperatureList" in data and data["temperatureList"]:
                    temperature = data["temperatureList"][0].get("value")
                    return temperature
                else:
                    _LOGGER.error("Temperature list is missing or empty in the API response.")
                    return None
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Error retrieving temperature: {e}")
            return None

    async def get_current_preset(self):
        """Retrieve the current preset mode."""
        if not self.token or not self.system_id:
            await self.login()
            await self.get_system_id()

        data_url = self.base_url + f"system/cosy-live-data/{self.system_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with self.session.get(data_url, headers=headers) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to get preset: {response.status} - {await response.text()}")
                data = await response.json()
                if "controllerStatusList" in data and data["controllerStatusList"]:
                    mode = data["controllerStatusList"][0].get("currentMode")
                    return {0: "hibernate", 1: "slumber", 2: "comfy", 3: "cosy"}.get(mode, "unknown")
                else:
                    raise ValueError("Preset mode data not available")
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Error retrieving preset mode: {e}")

    async def update(self):
        """Retrieve the current state (temperature and preset mode)."""
        try:
            current_temp = await self.get_current_temperature()
            current_mode = await self.get_current_preset()
            return {"current_temp": current_temp, "current_mode": current_mode}
        except Exception as e:
            raise RuntimeError(f"Error updating Cosy API: {e}")

    @property
    def unique_id(self):
        """Generate a unique ID using system_id."""
        if not self.system_id:
            raise RuntimeError("System ID not available")
        return f"cosy_thermostat_{self.system_id}"
