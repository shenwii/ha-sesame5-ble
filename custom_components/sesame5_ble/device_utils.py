"""Common helpers for Sesame BLE device readiness and method execution."""

from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


def _get_ready_lock(device: Any) -> asyncio.Lock:
    """Return a per-device lock so setup and refresh do not race each other on login."""
    lock = getattr(device, "_sesame_ready_lock", None)
    if lock is None:
        lock = asyncio.Lock()
        setattr(device, "_sesame_ready_lock", lock)
    return lock


def _get_command_lock(device: Any) -> asyncio.Lock:
    """Return a per-device lock so lock/unlock actions are serialized."""
    lock = getattr(device, "_sesame_command_lock", None)
    if lock is None:
        lock = asyncio.Lock()
        setattr(device, "_sesame_command_lock", lock)
    return lock


async def _async_await_if_needed(result: Any) -> Any:
    """Await a result when it is awaitable, otherwise return it unchanged."""
    if inspect.isawaitable(result):
        return await result
    return result


async def ensure_device_ready(device: Any, secret_key: str | None = None, *, address: str | None = None) -> None:
    """Ensure the device is connected and logged in before use."""
    if device is None:
        return

    secret_key = secret_key if secret_key is not None else getattr(device, "secret_key", None)
    if secret_key is None:
        raise ValueError("Missing SECRET_KEY for Sesame device")

    if getattr(device, "secret_key", None) is None:
        try:
            setattr(device, "secret_key", secret_key)
        except Exception:
            pass

    ready_lock = _get_ready_lock(device)
    async with ready_lock:
        connected = bool(getattr(device, "is_connected", False))
        logged_in = bool(getattr(device, "is_logged_in", False))
        if connected and logged_in:
            return

        if not connected:
            connect_method = getattr(device, "connect", None)
            if connect_method is not None:
                try:
                    await _async_await_if_needed(connect_method())
                except Exception as err:
                    LOGGER.debug(
                        "Reconnect failed for Sesame device %s: %s",
                        address or getattr(device, "address", "unknown"),
                        err,
                    )
                    raise

        if not getattr(device, "is_logged_in", False):
            login_method = getattr(device, "login", None)
            if login_method is not None:
                try:
                    await _async_await_if_needed(login_method(secret_key))
                except Exception:
                    LOGGER.warning(
                        "Login failed for Sesame device %s; secret key may be stale or invalid",
                        address or getattr(device, "address", "unknown"),
                    )
                    raise


async def async_command_lock_state(
    device: Any,
    *,
    target_locked: bool,
    history_name: str = "homeassistant",
    force: bool = False,
    secret_key: str | None = None,
    address: str | None = None,
    coordinator: Any | None = None,
) -> None:
    """Execute a lock/unlock command.

    State updates are produced by the gomalock callback path; this helper only
    triggers the action and defers coordinator refresh to the library callback.
    """
    if device is None:
        return

    command_lock = _get_command_lock(device)
    async with command_lock:
        current_status = getattr(device, "mech_status", None)
        current_locked = bool(getattr(current_status, "is_in_lock_range", False))
        if not force and current_locked == target_locked:
            return

        if not getattr(device, "is_connected", False) or not getattr(device, "is_logged_in", False):
            if not force:
                return
            await ensure_device_ready(device, secret_key, address=address)

        method_name = "lock" if target_locked else "unlock"
        await async_call_device_method(device, method_name, history_name)


async def async_call_device_method(device: Any, method_name: str, *args: Any, **kwargs: Any) -> Any:
    """Call a device method regardless of whether it is sync or async."""
    method = getattr(device, method_name, None)
    if method is None:
        raise AttributeError(f"Sesame device does not support method '{method_name}'")
    result = method(*args, **kwargs)
    return await _async_await_if_needed(result)


async def async_set_lock_position(
    device: Any,
    lock_position: int,
    unlock_position: int,
    *,
    secret_key: str | None = None,
    address: str | None = None,
    coordinator: Any | None = None,
) -> None:
    """Set the Sesame lock and unlock position thresholds after ensuring readiness."""
    if device is None:
        return

    if not getattr(device, "is_connected", False) or not getattr(device, "is_logged_in", False):
        await ensure_device_ready(device, secret_key, address=address)

    await async_call_device_method(device, "set_lock_position", int(lock_position), int(unlock_position))
