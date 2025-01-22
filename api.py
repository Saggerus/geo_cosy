import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class CosyAPI:
    def __init__(self, username, password):
        self.base_url = "https://cosy.geotogether.com/api/userapi/"
        self.username = username
        self.password = password
        self.token = None
        self.system_id = None

    async def login(self):
        login_url = self.base_url + "account/login"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(login_url, json={"name": self.username, "emailAddress": self.username, "password": self.password}) as response:
                    if response.status == 401:
                        _LOGGER.error("Unauthorized: Check your username and password")
                    response.raise_for_status()
                    data = await response.json()
                    self.token = data["token"]
                    _LOGGER.debug("Login successful, token retrieved")
                    return self.token
            except aiohttp.ClientError as e:
                _LOGGER.error("Error during login: %s, message='%s', url='%s'", e.status, e.message, e.request_info.url)
                return None

    async def get_system_id(self):
        data_url = self.base_url + "user/detail-systems?peripherals=true"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(data_url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                self.system_id = data["systemRoles"][0]["systemId"]
                _LOGGER.debug("System ID retrieved: %s", self.system_id)

    async def get_current_temperature(self):
        data_url = self.base_url + f"system/cosy-live-data/{self.system_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(data_url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                temperature = data["temperatureList"][0]["value"]
                _LOGGER.debug("Current temperature retrieved: %s", temperature)
                return temperature

    async def get_current_preset(self):
        data_url = self.base_url + f"system/cosy-live-data/{self.system_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(data_url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                preset = data["controllerStatusList"][0]["currentMode"]
                _LOGGER.debug("Current preset mode retrieved: %s", preset)
                return preset

    async def set_preset_mode(self, mode):
        if mode == "slumber":
            set_mode_url = self.base_url + f"system/cosy-cancelallevents/{self.system_id}?zone=0"
            headers = {"Authorization": f"Bearer {self.token}"}
            async with aiohttp.ClientSession() as session:
                async with session.delete(set_mode_url, headers=headers) as response:
                    response.raise_for_status()
                    _LOGGER.debug("Preset mode set to %s", mode)
        else:
            mode_id = {"comfy": 2, "cosy": 3}.get(mode, 0)
            set_mode_url = self.base_url + f"system/cosy-adhocmode/{self.system_id}"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            payload = {
                "modeId": mode_id,
                "startOffset": 0,
                "duration": 60,  # Default duration, can be adjusted
                "welcomeHomeActive": False,
                "zone": "0"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(set_mode_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    _LOGGER.debug("Preset mode set to %s", mode)

    async def set_target_temperature(self, mode, temperature):
        data_url = self.base_url + f"system/cosy-live-data/{self.system_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(data_url, headers=headers, json={"mode": mode, "temperature": temperature}) as response:
                response.raise_for_status()
                _LOGGER.debug("Target temperature set to %s for mode %s", temperature, mode)

    async def set_hibernate_mode(self, state):
        data_url = self.base_url + f"system/cosy-instandby/{self.system_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(data_url, headers=headers, json={"value": state}) as response:
                response.raise_for_status()
                _LOGGER.debug("Hibernate mode set to %s", state)