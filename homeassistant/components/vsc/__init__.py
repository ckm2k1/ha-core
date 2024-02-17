"""The VeSync Devices integration."""
from __future__ import annotations

from pyvesync import VeSync

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.HUMIDIFIER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VeSync Devices from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    manager = VeSync(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        time_zone="EST",  # TODO: switch to config flow
    )

    if not await hass.async_add_executor_job(manager.login):
        return False

    hass.data[DOMAIN] = manager

    await hass.async_add_executor_job(manager.update)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data.pop(DOMAIN)
    return unload_ok
