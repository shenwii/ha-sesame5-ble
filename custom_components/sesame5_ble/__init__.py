"""The Sesame 5 BLE integration."""

from __future__ import annotations

import logging
from typing import Any

import gomalock
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import SesameCoordinator
from .device_utils import async_command_lock_state, async_set_lock_position, ensure_device_ready

LOGGER = logging.getLogger(__name__)

from .const import DOMAIN

PLATFORMS: list[Platform] = [
    Platform.LOCK,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

SERVICE_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): str,
    vol.Optional("lock_position"): int,
    vol.Optional("unlock_position"): int,
})

CONFIG_SCHEMA = cv.config_entry_only_config_schema

type SesameConfigEntry = ConfigEntry[SesameCoordinator]


async def _async_force_entry_action(hass: HomeAssistant, entry: SesameConfigEntry, *, target_locked: bool) -> None:
    """Force a single config entry to the requested lock state."""
    coordinator = entry.runtime_data
    if coordinator is None:
        coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    if coordinator.device_kind() != "lock":
        return

    device = coordinator.device
    if device is None:
        return
    
    await async_command_lock_state(
        device,
        target_locked=target_locked,
        history_name="homeassistant",
        force=True,
        coordinator=coordinator,
    )


async def _async_force_device_action(hass: HomeAssistant, *, target_locked: bool, entry_id: str | None = None) -> None:
    """Force the lock into the requested state for the selected Sesame entry.

    A service may target all configured entries or a specific one. Button entities
    call the per-entry helper directly to avoid the extra list/filter loop.
    """
    entries = hass.config_entries.async_entries(DOMAIN)
    if entry_id is not None:
        entries = [entry for entry in entries if entry.entry_id == entry_id]

    for entry in entries:
        await _async_force_entry_action(hass, entry, target_locked=target_locked)


async def _async_force_lock_service(hass: HomeAssistant, call) -> None:
    """Service handler for a forced lock action."""
    await _async_force_device_action(hass, target_locked=True, entry_id=call.data.get("entry_id"))


async def _async_force_unlock_service(hass: HomeAssistant, call) -> None:
    """Service handler for a forced unlock action."""
    await _async_force_device_action(hass, target_locked=False, entry_id=call.data.get("entry_id"))


async def _async_set_lock_position_service(hass: HomeAssistant, call) -> None:
    """Set lock/unlock position thresholds for selected Sesame entries."""
    entry_id = call.data.get("entry_id")
    lock_position = call.data.get("lock_position")
    unlock_position = call.data.get("unlock_position")

    if lock_position is None or unlock_position is None:
        LOGGER.warning("Ignoring set_lock_position service call without both lock_position and unlock_position")
        return

    entries = hass.config_entries.async_entries(DOMAIN)
    if entry_id is not None:
        entries = [entry for entry in entries if entry.entry_id == entry_id]

    for entry in entries:
        coordinator = entry.runtime_data or hass.data.get(DOMAIN, {}).get(entry.entry_id)

        if coordinator.device_kind() != "lock":
            continue
        
        device = coordinator.device
        if device is None:
            continue

        try:
            await async_set_lock_position(
                device,
                lock_position,
                unlock_position,
                coordinator=coordinator,
            )
        except Exception as err:
            LOGGER.warning("Unable to set lock position on %s: %s", entry.entry_id, err)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Register Sesame services."""
    if not hass.services.has_service(DOMAIN, "lock"):
        hass.services.async_register(DOMAIN, "lock", _async_force_lock_service, schema=SERVICE_SCHEMA)
    if not hass.services.has_service(DOMAIN, "unlock"):
        hass.services.async_register(DOMAIN, "unlock", _async_force_unlock_service, schema=SERVICE_SCHEMA)
    if not hass.services.has_service(DOMAIN, "set_lock_position"):
        hass.services.async_register(DOMAIN, "set_lock_position", _async_set_lock_position_service, schema=SERVICE_SCHEMA)
    return True


async def _async_prepare_device(device: Any, entry: SesameConfigEntry) -> None:
    """Check current runtime state first, then prefer login before connect."""
    secret_key = entry.data.get("secret_key")
    if not secret_key:
        raise ValueError("Missing SECRET_KEY for Sesame device")

    await ensure_device_ready(
        device,
        secret_key
    )


async def _async_discover_device_by_address(address: str) -> Any | None:
    """Return the discovered gomalock device object for the given address when available."""
    try:
        discovered = await gomalock.SesameScanner.discover(timeout=5)
    except Exception:
        return None

    if not discovered:
        return None

    for found in discovered.values():
        if str(getattr(found, "address", "")).lower() == str(address).lower():
            return found
    return None


async def _async_create_gomalock_device(entry: SesameConfigEntry) -> Any:
    """Create a gomalock device from a discovered BLE object when possible."""
    address = str(entry.data[CONF_ADDRESS])
    model = str(entry.data.get("model", "")).lower()
    secret_key = entry.data.get("secret_key")
    device_cls = gomalock.SesameTouch if "touch" in model else gomalock.Sesame5

    discovered = await _async_discover_device_by_address(address)
    if discovered is not None:
        try:
            if secret_key:
                return device_cls(discovered, secret_key=secret_key)
            return device_cls(discovered)
        except TypeError:
            pass

    if secret_key:
        return device_cls(address, secret_key=secret_key, reconnect_attempts=3)
    return device_cls(address, reconnect_attempts=3)


async def async_setup_entry(hass: HomeAssistant, entry: SesameConfigEntry) -> bool:
    """Set up a Sesame config entry from a config entry."""
    device = await _async_create_gomalock_device(entry)

    try:
        await _async_prepare_device(device, entry)
    except Exception as err:
        LOGGER.warning(
            "Setup for Sesame device %s deferred until the lock is in range: %s",
            entry.data.get(CONF_ADDRESS),
            err,
        )
        raise ConfigEntryNotReady from err

    coordinator = SesameCoordinator(hass, device, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        LOGGER.exception("Failed to connect to Sesame BLE device %s", entry.data.get(CONF_ADDRESS))
        await coordinator.shutdown()
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SesameConfigEntry) -> bool:
    """Unload a Sesame config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        await entry.runtime_data.shutdown()
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate older config entries to the current version."""
    version = config_entry.version

    if version == 1:
        config_entry.version = 1
        return True

    return True
