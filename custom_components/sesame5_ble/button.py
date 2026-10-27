"""Button platform for Sesame devices."""

from __future__ import annotations

import logging
from typing import Any


from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SesameConfigEntry, _async_force_entry_action
from .const import DOMAIN

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SesameConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add force lock/unlock buttons for lock entries only."""
    coordinator = entry.runtime_data
    if coordinator.data.get("device_kind") != "lock":
        return

    LOGGER.debug("Registering Sesame force buttons for %s (%s)", entry.entry_id, type(coordinator).__name__)
    async_add_entities(
        [
            SesameForceLockButton(entry, coordinator),
            SesameForceUnlockButton(entry, coordinator),
        ]
    )


class SesameForceButtonBase(ButtonEntity):
    """Common base for Sesame force actions."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data.get("address", entry.entry_id))},
            "name": f"Sesame {entry.data.get('model', 'Device')}",
            "manufacturer": "Sesame",
            "model": entry.data.get("model", "Sesame"),
            "connections": {("mac", entry.data.get("address", ""))},
        }


class SesameForceLockButton(SesameForceButtonBase):
    """Force a Sesame lock to lock without checking current state."""

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        super().__init__(entry, coordinator)
        self._attr_unique_id = f"{entry.entry_id}_force_lock"
        self._attr_name = "Force Lock"
        self._attr_icon = "mdi:lock"

    async def async_press(self) -> None:
        """Press the button to force the lock to lock."""
        await _async_force_entry_action(
            self._coordinator.hass,
            self._entry,
            target_locked=True,
        )


class SesameForceUnlockButton(SesameForceButtonBase):
    """Force a Sesame lock to unlock without checking current state."""

    def __init__(self, entry: ConfigEntry, coordinator: Any) -> None:
        super().__init__(entry, coordinator)
        self._attr_unique_id = f"{entry.entry_id}_force_unlock"
        self._attr_name = "Force Unlock"
        self._attr_icon = "mdi:lock-open-variant"

    async def async_press(self) -> None:
        """Press the button to force the lock to unlock."""
        await _async_force_entry_action(
            self._coordinator.hass,
            self._entry,
            target_locked=False,
        )
