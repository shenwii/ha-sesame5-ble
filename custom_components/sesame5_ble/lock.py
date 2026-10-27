"""Lock platform for Sesame devices."""

from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, SesameConfigEntry
from .device_utils import async_command_lock_state


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SesameConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the lock platform for lock devices only."""
    coordinator = entry.runtime_data
    if coordinator.data.get("device_kind") != "lock":
        return
    entity = SesameLockEntity(entry, coordinator)
    coordinator.async_add_listener(entity.async_write_ha_state)
    async_add_entities([entity])


class SesameLockEntity(LockEntity):
    """Representation of a Sesame lock."""

    _attr_has_entity_name = True
    _attr_device_class = "door"

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_lock"
        self._attr_name = "Sesame Lock"
        self._attr_device_info = {
            "identifiers": {("sesame5_ble", entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }

    @property
    def _history_name(self) -> str:
        """Return a stable identifier for the gomalock action history entry."""
        return "homeassistant"

    @property
    def is_locked(self) -> bool | None:
        """Return whether the lock is locked."""
        state = self._coordinator.data
        if not isinstance(state, dict):
            return None
        if "is_locked" in state:
            return bool(state.get("is_locked"))
        if "locked" in state:
            return bool(state.get("locked"))
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose additional lock status details."""
        state = self._coordinator.data
        if not isinstance(state, dict):
            return {}
        attrs: dict[str, Any] = {}
        for key in (
            "device_status",
            "connection_status",
            "connected",
            "logged_in",
            "battery",
            "battery_voltage",
            "position",
            "target",
            "is_stop",
            "is_in_lock_range",
            "is_in_unlock_range",
            "is_background_reconnecting",
        ):
            if key in state:
                attrs[key] = state[key]
        return attrs

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the Sesame device."""
        await async_command_lock_state(
            self._coordinator.device,
            target_locked=True,
            history_name=self._history_name,
            force=False,
            secret_key=self._entry.data.get("secret_key"),
            address=str(getattr(self._coordinator.device, "address", "unknown")),
            coordinator=self._coordinator,
        )

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the Sesame device."""
        await async_command_lock_state(
            self._coordinator.device,
            target_locked=False,
            history_name=self._history_name,
            force=False,
            secret_key=self._entry.data.get("secret_key"),
            address=str(getattr(self._coordinator.device, "address", "unknown")),
            coordinator=self._coordinator,
        )

    async def async_open(self, **kwargs: Any) -> None:
        """Open the Sesame device if supported."""
        await async_command_lock_state(
            self._coordinator.device,
            target_locked=False,
            history_name=self._history_name,
            force=False,
            secret_key=self._entry.data.get("secret_key"),
            address=str(getattr(self._coordinator.device, "address", "unknown")),
            coordinator=self._coordinator,
        )
