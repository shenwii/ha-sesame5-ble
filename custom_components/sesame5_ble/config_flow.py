"""Config flow for the Sesame 5 BLE integration."""

from __future__ import annotations

from typing import Any

import gomalock
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN


def _device_factory(model: str) -> type[Any]:
    """Return the gomalock device class matching the discovered model."""
    model_name = (model or "").lower()
    if "touch" in model_name:
        return gomalock.SesameTouch
    return gomalock.Sesame5


def _model_name(device: Any) -> str:
    """Return a readable model label from the discovered device."""
    advertisement = getattr(device, "advertisement_data", None)
    product_model = getattr(advertisement, "product_model", None)
    if product_model is not None:
        name = getattr(product_model, "name", None)
        if name is not None:
            return str(name)
    return getattr(device, "model", "Sesame")


class Sesame5BleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Sesame device config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_devices: dict[str, dict[str, Any]] = {}
        self._selected_device: dict[str, Any] | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow for this config entry."""
        return Sesame5BleOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Discover nearby Sesame devices and let the user choose one."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            self._selected_device = self._discovered_devices.get(address)
            if self._selected_device is None:
                return self.async_abort(reason="device_not_found")
            if self._selected_device["registered"]:
                return await self.async_step_secret_key()
            return await self.async_step_register_confirm()

        discovered = await gomalock.SesameScanner.discover(timeout=10)
        if not discovered:
            return self.async_abort(reason="no_devices_found")

        self._discovered_devices = {}
        for found in discovered.values():
            advertisement = getattr(found, "advertisement_data", None)
            address = str(found.address)
            uuid = getattr(advertisement, "device_uuid", None)
            if uuid is None:
                uuid = address
            self._discovered_devices[address] = {
                "address": address,
                "model": _model_name(found),
                "registered": bool(getattr(advertisement, "is_registered", False)),
                "uuid": str(uuid),
            }

        options = {
            address: (
                f"{info['address']} | model={info['model']} | "
                f"registered={str(info['registered']).lower()} | uuid={info['uuid']}"
            )
            for address, info in self._discovered_devices.items()
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(options)}),
        )

    async def async_step_register_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask whether to register a new Sesame device with gomalock."""
        if self._selected_device is None:
            return self.async_abort(reason="device_not_found")

        if user_input is not None:
            if not user_input.get("register", False):
                return self.async_abort(reason="not_registered")

            address = self._selected_device["address"]
            model = self._selected_device["model"]
            device_cls = _device_factory(model)
            try:
                async with device_cls(address) as sesame_device:
                    secret_key = await sesame_device.register()
            except Exception:
                return self.async_abort(reason="register_failed")

            data = {
                "address": address,
                "model": model,
                "registered": True,
                "uuid": self._selected_device["uuid"],
                "secret_key": secret_key,
            }
            await self.async_set_unique_id(data["uuid"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"{model} {address}", data=data)

        return self.async_show_form(
            step_id="register_confirm",
            data_schema=vol.Schema({vol.Required("register", default=True): bool}),
        )

    async def async_step_secret_key(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask for the secret key for an already registered Sesame device."""
        if self._selected_device is None:
            return self.async_abort(reason="device_not_found")

        if user_input is not None:
            secret_key = str(user_input["secret_key"]).strip()
            if not secret_key:
                return self.async_abort(reason="invalid_secret_key")

            data = {
                "address": self._selected_device["address"],
                "model": self._selected_device["model"],
                "registered": True,
                "uuid": self._selected_device["uuid"],
                "secret_key": secret_key,
            }
            await self.async_set_unique_id(data["uuid"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"{data['model']} {data['address']}", data=data)

        return self.async_show_form(
            step_id="secret_key",
            data_schema=vol.Schema({vol.Required("secret_key"): str}),
        )


class Sesame5BleOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Placeholder options flow."""
        return self.async_create_entry(title="", data={})
