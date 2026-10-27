"""Sensor platform for Sesame devices."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEGREE, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, SesameConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SesameConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform with device-specific sensors."""
    coordinator = entry.runtime_data
    device_kind = coordinator.data.get("device_kind")

    entities: list[SensorEntity] = []
    if device_kind == "lock":
        entities.extend(
            [
                SesameBatterySensor(entry, coordinator),
                SesameLockPositionSensor(entry, coordinator),
                SesameLockThresholdSensor(entry, coordinator),
                SesameUnlockThresholdSensor(entry, coordinator),
            ]
        )
    elif device_kind == "touch":
        entities.extend(
            [
                SesameTouchBatterySensor(entry, coordinator),
                SesameTouchCardCountSensor(entry, coordinator),
                SesameTouchFingerprintCountSensor(entry, coordinator),
                SesameTouchPasswordCountSensor(entry, coordinator),
            ]
        )

    if not entities:
        return

    for entity in entities:
        coordinator.async_add_listener(entity.async_write_ha_state)

    async_add_entities(entities)


class SesameBatterySensor(SensorEntity):
    """Battery percentage sensor for Sesame lock devices."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_battery"
        self._attr_name = "Battery"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def native_value(self) -> float | None:
        """Return the current battery level for lock devices."""
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        battery = state.get("battery")
        if battery is None:
            return None
        return float(battery)

    @property
    def available(self) -> bool:
        """Return whether the sensor is available."""
        return self._coordinator.last_update_success


class SesameTouchBatterySensor(SensorEntity):
    """Battery percentage sensor for Sesame Touch devices."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_touch_battery"
        self._attr_name = "Battery"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def native_value(self) -> float | None:
        """Return the current battery percentage for touch devices."""
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        if "battery" in state:
            return float(state["battery"])
        return None

    @property
    def available(self) -> bool:
        """Return whether the sensor is available."""
        return self._coordinator.last_update_success


class SesameTouchCardCountSensor(SensorEntity):
    """Number of saved cards on the touch."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_touch_cards"
        self._attr_name = "Cards Number"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def native_value(self) -> int | None:
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        return state.get("card_count")

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success


class SesameTouchFingerprintCountSensor(SensorEntity):
    """Number of saved fingerprints on the touch."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_touch_fingerprints"
        self._attr_name = "Fingerprints Number"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def native_value(self) -> int | None:
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        return state.get("fingerprint_count")

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success


class SesameTouchPasswordCountSensor(SensorEntity):
    """Number of saved passwords on the touch."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_touch_passwords"
        self._attr_name = "Passwords Number"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def native_value(self) -> int | None:
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        return state.get("password_count")

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success


class SesameLockPositionSensor(SensorEntity):
    """Current mechanical position sensor for Sesame lock devices."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_position"
        self._attr_name = "Position"
        self._attr_icon = "mdi:angle-acute"
        self._attr_native_unit_of_measurement = DEGREE
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def native_value(self) -> int | None:
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        value = state.get("position")
        return int(value) if value is not None else None

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success


class SesameLockThresholdSensor(SensorEntity):
    """Configured lock-position threshold sensor for Sesame lock devices."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_lock_position"
        self._attr_name = "Lock Position"
        self._attr_icon = "mdi:angle-acute"
        self._attr_native_unit_of_measurement = DEGREE
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def native_value(self) -> int | None:
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        value = state.get("lock_position")
        return int(value) if value is not None else None

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success


class SesameUnlockThresholdSensor(SensorEntity):
    """Configured unlock-position threshold sensor for Sesame lock devices."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_unlock_position"
        self._attr_name = "Unlock Position"
        self._attr_icon = "mdi:angle-acute"
        self._attr_native_unit_of_measurement = DEGREE
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def native_value(self) -> int | None:
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        value = state.get("unlock_position")
        return int(value) if value is not None else None

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success
