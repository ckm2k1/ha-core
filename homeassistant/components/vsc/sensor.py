"""Humidifier sensors."""
from pyvesync.vesyncfan import VeSyncSuperior6000S

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory

# from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


# See cover.py for more details.
# Note how both entities for each roller sensor (battry and illuminance) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    manager = hass.data[DOMAIN]

    sensors: list[SensorEntity] = []
    for fan in manager.fans:
        sensors.append(TemperatureSensor(fan))
        sensors.append(FilterLifeSensor(fan))

    if sensors:
        async_add_entities(sensors)


class HumidifierSensorMixin(SensorEntity):
    """Base class for humidifier sensors."""

    def __init__(self, device: VeSyncSuperior6000S) -> None:
        """Initialize the sensor."""
        self.device = device

    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self.device.connection_status == "online"

    @property
    def device_info(self) -> DeviceInfo:
        """Return information to link this entity with the correct device."""
        return {
            "identifiers": {(DOMAIN, self.device.cid)},
            "name": "Indoor Temperature",
            "model": "Superior 6000S",
            "manufacturer": "Levoit",
        }


class TemperatureSensor(HumidifierSensorMixin):
    """Humidifier built-in temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Indoor Temperature"

    @property
    def unique_id(self) -> str:
        """Return sensor unique id."""
        return f"{self.device.cid}_temperature"

    @property
    def native_value(self) -> float | None:
        """Return current indoor temperature."""
        return self.device.temperature / 10


class FilterLifeSensor(HumidifierSensorMixin):
    """Humidifier filter life remaining."""

    _attr_device_class = None
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True
    _attr_name = "Filter life"
    _attr_icon = "mdi:filter"

    @property
    def unique_id(self) -> str:
        """Return sensor unique id."""
        return f"{self.device.cid}_filter_life"

    @property
    def native_value(self) -> int:
        """Return the percentage of remaining filter life."""
        return self.device.filter_life
