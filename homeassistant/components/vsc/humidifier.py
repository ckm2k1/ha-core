"""VeSync Humidifier general platform."""
from typing import Any

from pyvesync.vesyncfan import VeSyncSuperior6000S

from homeassistant.components.humidifier import (
    MODE_AUTO,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

MODE_MANUAL = "manual"
MODE_HUMIDITY = "humidity"
MODE_SLEEP = "sleep"

HUMIDIFIER_MODES = {
    "humidity": MODE_HUMIDITY,
    "manual": MODE_MANUAL,
    "sleep": MODE_SLEEP,
    "auto": MODE_AUTO,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Do platform entry setup."""
    manager = hass.data[DOMAIN]
    devices = []
    for f in manager.fans:
        devices.append(VeSyncHumidifier(f))

    async_add_entities(devices)


class VeSyncHumidifier(HumidifierEntity):
    """Base VeSync humidifier device."""

    _attr_supported_features = HumidifierEntityFeature.MODES
    _attr_available_modes = [MODE_HUMIDITY, MODE_MANUAL, MODE_AUTO, MODE_SLEEP]
    _attr_has_entity_name = True
    _attr_name = None
    _attr_max_humidity = 80
    _attr_min_humidity = 30

    def __init__(self, device: VeSyncSuperior6000S) -> None:
        """Initialize the humidifier device."""
        self.humidifier = device
        self._attr_unique_id = f"{self.humidifier.cid}_humidifier"
        self._attr_entity_picture = self.humidifier.device_image

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.humidifier.cid)},
            "model": self.humidifier.device_type,
            "manufacturer": "Levoit",
            "name": self.humidifier.device_name,
        }

    def update(self) -> None:
        """Fetch fresh data from VeSync API for the device."""
        self.humidifier.update()

    @property
    def is_on(self) -> bool | None:
        """Return True if the device is on."""
        return self.humidifier.device_status == "on"

    @property
    def available_modes(self) -> list[str]:
        """Return all available humidifier modes."""
        return list(HUMIDIFIER_MODES.values())

    @property
    def mode(self) -> str:
        """Return current operational mode."""
        return HUMIDIFIER_MODES[self.humidifier.mode]

    @property
    def available(self) -> bool:
        """Return True if the device is online."""
        return self.humidifier.connection_status == "online"

    @property
    def target_humidity(self) -> int:
        """Return the currently set target humidity."""
        return self.humidifier.target_humidity

    @property
    def current_humidity(self) -> int:
        """Return the currently set target humidity."""
        return self.humidifier.humidity_level

    def set_mode(self, mode: str) -> None:
        """Set device operating mode."""
        if mode == MODE_AUTO:
            self.humidifier.set_auto_mode()
        elif mode == MODE_SLEEP:
            self.humidifier.set_humidity_mode("manual")
        elif mode == MODE_HUMIDITY:
            self.humidifier.set_humidity_mode("humidity")
        elif mode == MODE_MANUAL:
            self.humidifier.set_manual_mode()
        else:
            # Huh??
            return

    def set_humidity(self, humidity: int) -> None:
        """Set device target humidity."""
        self.humidifier.set_humidity(humidity)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn on the device."""
        self.humidifier.turn_on()

    def turn_off(self, **kwargs: Any) -> None:
        """Turn off the device."""
        self.humidifier.turn_off()
