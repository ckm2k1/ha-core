"""Humidifier sensors."""
from pyvesync.vesyncfan import VeSyncSuperior6000S

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

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

    new_devices = []
    for fan in manager.fans:
        new_devices.append(TemperatureSensor(fan))

    if new_devices:
        async_add_entities(new_devices)


# This is another sensor, but more simple compared to the battery above. See the
# comments above for how each field works.
class TemperatureSensor(SensorEntity):
    """Humidifier built-in temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    # _attr_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(self, device: VeSyncSuperior6000S) -> None:
        """Initialize the sensor."""
        self.device = device
        # As per the sensor, this must be a unique value within this domain. This is done
        # by using the device ID, and appending "_battery"
        self._attr_unique_id = f"{self.device.cid}_temperature"

        # The name of the entity
        # self._attr_name = f"{self.device.device_name} Temperature"

        # self.native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    @property
    def device_info(self) -> DeviceInfo:
        """Return information to link this entity with the correct device."""
        return {
            "identifiers": {(DOMAIN, self.device.cid)},
            "name": "Indoor Temperature",
            "model": "Superior 6000S",
            "manufacturer": "Levoit",
        }

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self.device.connection_status == "online"

    @property
    def native_value(self) -> float | None:
        """Return current indoor temperature."""
        return self.device.temperature / 10

    # @property
    # def state(self) -> float:
    #     """Return the state of the sensor."""
    #     return self.device.temperature / 10

    def update(self) -> None:
        """Update the sensor state."""
        self.device.update()
