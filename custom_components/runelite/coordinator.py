from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
import logging

_LOGGER = logging.getLogger(__name__)

class OsrsHighscoresCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch OSRS hiscores from RuneLite API."""
    def __init__(self, hass, username: str):
        self.username = username
        super().__init__(
            hass,
            _LOGGER,
            name=f"OSRS Highscores Coordinator ({username})",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        url = f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.json?player={self.username}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching data: {response.status}")
                    return await response.json(content_type=None)
        except Exception as err:
            _LOGGER.warning("Error fetching data from API: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}")

