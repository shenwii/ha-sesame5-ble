"""Binary sensor platform for Sesame devices.

This exposes the current lock state as a separate binary sensor for debugging and
visibility in Home Assistant, while the native `lock` entity remains the
authoritative control endpoint.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SesameConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SesameConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the lock-state binary sensor for lock devices only."""
    coordinator = entry.runtime_data
    if coordinator.data.get("device_kind") != "lock":
        return

    entity = SesameLockStateBinarySensor(entry, coordinator)
    coordinator.async_add_listener(entity.async_write_ha_state)
    async_add_entities([entity])


class SesameLockStateBinarySensor(BinarySensorEntity):
    """Expose the current Sesame lock state as a binary sensor for debugging."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.LOCK

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_lock_state"
        self._attr_name = "Lock State"
        self._attr_device_info = {
            "identifiers": {("sesame5_ble", entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def is_on(self) -> bool | None:
        """Return the lock state in the UI-friendly polarity.

        The underlying gomalock value is `is_locked`, but the HA lock binary sensor
        is easier to read when the boolean is inverted for display.
        """
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        if "is_locked" in state:
            return not bool(state.get("is_locked"))
        if "locked" in state:
            return not bool(state.get("locked"))
        return None

    @property
    def available(self) -> bool:
        """Return whether the sensor is available."""
        return self._coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Provide extra state for debugging."""
        state = self._coordinator.data
        if not isinstance(state, dict):
            return {}
        return {
            "device_status": state.get("device_status"),
            "battery": state.get("battery"),
            "connected": state.get("connected"),
            "logged_in": state.get("logged_in"),
        }
