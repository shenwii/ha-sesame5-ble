"""Coordinator for Sesame BLE devices."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

LOGGER = logging.getLogger(__name__)

DOMAIN = "sesame5_ble"


class SesameCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate state updates for a Sesame device."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Any,
        entry: ConfigEntry,
    ) -> None:
        self.device = device
        self.entry = entry
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=None,
        )
        self._attach_device_callbacks()

    def device_kind(self) -> str:
        """Return the device category used for state normalization."""
        model = str(getattr(self.device, "model", self.entry.data.get("model", ""))).lower()
        if "touch" in model:
            return "touch"
        return "lock"

    def _coerce_battery(self, value: Any) -> Any:
        """Convert the fixed gomalock battery percentage to a float when available."""
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return value

    def _base_device_state(self, device_obj: Any | None = None) -> dict[str, Any]:
        """Common metadata for every device."""
        device = device_obj if device_obj is not None else self.device
        if device is None:
            return {}

        state: dict[str, Any] = {
            "device_kind": self.device_kind(),
            "address": getattr(device, "address", None),
            "model": getattr(device, "model", None),
            "connected": bool(getattr(device, "is_connected", False)),
            "logged_in": bool(getattr(device, "is_logged_in", False)),
        }

        advertisement_data = getattr(device, "advertisement_data", None)
        if advertisement_data is not None:
            product_model = getattr(advertisement_data, "product_model", None)
            if product_model is not None:
                state["model"] = getattr(product_model, "name", str(product_model))
            state["registered"] = bool(getattr(advertisement_data, "is_registered", False))
            state["uuid"] = getattr(advertisement_data, "device_uuid", None)

        device_status = getattr(device, "device_status", None)
        if device_status is not None:
            state["connection_status"] = str(getattr(device_status, "name", device_status))

        return state

    def _touch_state(self, status_obj: Any, state: dict[str, Any]) -> dict[str, Any]:
        """Fixed fields for Touch devices."""
        state["device_status"] = str(getattr(status_obj, "name", status_obj))
        state["card_count"] = getattr(status_obj, "card_count", None)
        state["fingerprint_count"] = getattr(status_obj, "fingerprint_count", None)
        state["password_count"] = getattr(status_obj, "password_count", None)
        state["battery_voltage"] = getattr(status_obj, "battery_voltage", None)
        state["battery"] = self._coerce_battery(getattr(status_obj, "battery_percentage", None))
        state["battery_critical"] = getattr(status_obj, "is_battery_critical", None)
        return state

    def _lock_state(self, status_obj: Any, state: dict[str, Any]) -> dict[str, Any]:
        """Fixed fields for lock devices."""
        is_in_lock_range = getattr(status_obj, "is_in_lock_range", None)
        is_in_unlock_range = getattr(status_obj, "is_in_unlock_range", None)
        if is_in_lock_range is None and is_in_unlock_range is not None:
            is_in_lock_range = not bool(is_in_unlock_range)

        state["is_locked"] = bool(is_in_lock_range)
        state["locked"] = bool(is_in_lock_range)
        state["device_status"] = "locked" if bool(is_in_lock_range) else "unlocked"
        state["position"] = getattr(status_obj, "position", None)
        state["target"] = getattr(status_obj, "target", None)
        state["is_stop"] = getattr(status_obj, "is_stop", None)
        state["is_in_lock_range"] = is_in_lock_range
        state["is_in_unlock_range"] = is_in_unlock_range
        state["battery_voltage"] = getattr(status_obj, "battery_voltage", None)
        state["battery"] = self._coerce_battery(getattr(status_obj, "battery_percentage", None))
        state["battery_critical"] = getattr(status_obj, "is_battery_critical", None)
        state["_raw_battery"] = getattr(status_obj, "_raw_battery", None)
        state["_status_flags"] = getattr(status_obj, "_status_flags", None)

        mech_setting = getattr(self.device, "mech_setting", None)
        if mech_setting is not None:
            state["lock_position"] = getattr(mech_setting, "lock_position", None)
            state["unlock_position"] = getattr(mech_setting, "unlock_position", None)
            state["auto_lock_duration"] = getattr(mech_setting, "auto_lock_duration", None)

        return state

    def _normalize_state(self) -> dict[str, Any]:
        """Fallback state normalization used when no callback payload is available."""
        state = self._base_device_state()
        if not state:
            return {"device_kind": self.device_kind()}

        if self.device_kind() == "touch":
            touch_status = getattr(self.device, "device_status", None)
            if touch_status is None:
                state["device_status"] = "unknown"
                return state
            return self._touch_state(touch_status, state)

        mech_status = getattr(self.device, "mech_status", None)
        if mech_status is None:
            state["device_status"] = "not_logged_in"
            state["locked"] = None
            state["is_locked"] = None
            return state

        return self._lock_state(mech_status, state)

    def _normalize_state_from_status(self, device_obj: Any | None, status_obj: Any | None) -> dict[str, Any]:
        """Normalize the exact callback payload from gomalock into HA state."""
        state = self._base_device_state(device_obj)
        if status_obj is None:
            return state

        if self.device_kind() == "touch":
            return self._touch_state(status_obj, state)

        return self._lock_state(status_obj, state)

    def _make_callback_wrapper(self):
        """Wrap the original callback so HA updates are triggered without dropping the library callback."""
 
        def _wrapper(device_obj: Any | None, status_obj: Any | None) -> None:
            state = self._normalize_state_from_status(device_obj, status_obj)
            self.hass.add_job(self.async_set_updated_data, state)

        return _wrapper

    def _attach_device_callbacks(self) -> None:
        """Attach gomalock callbacks to update HA state in real time."""
        if self.device is None:
            return
        self.device.register_mech_status_callback(self._make_callback_wrapper())

    async def _async_update_data(self) -> dict[str, Any]:
        """Read the latest state from the gomalock device.

        The authoritative state for Sesame BLE devices is produced by the library
        when it decodes Bluetooth advertisements / status callbacks. We do not
        force a connect-and-refresh for every tick; that defeats low-power BLE.
        """
        if self.device is None:
            return {}

        return self._normalize_state()

    async def shutdown(self) -> None:
        """Close any active BLE resources."""
        close_method = getattr(self.device, "close", None)
        if close_method is not None:
            try:
                await close_method()
            except Exception:  # pragma: no cover
                LOGGER.debug("Failed to close Sesame device %s", self.device)
