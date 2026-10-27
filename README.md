# ha-sesame5-ble

![Sesame 5 BLE banner](custom_components/sesame5_ble/brand/logo.svg)

Home Assistant custom integration for Sesame BLE locks and Touch devices using the `gomalock` Python library.

This project is built for a local-first, low-power Bluetooth workflow. State updates are driven by the native `gomalock` callback payload, while lock/unlock commands remain a separate action path.

## Marketplace-ready brand assets

The repository includes a white-background visual set designed for GitHub, HACS, and marketplace presentation:

- `custom_components/sesame5_ble/brand/icon.svg` — Home Assistant component icon variants
- `custom_components/sesame5_ble/brand/logo.svg` wide banner for README and project headers

## Release summary

This integration is designed for a stable, low-power Sesame BLE workflow:

- Discover nearby devices with `gomalock.SesameScanner.discover`
- Add a device through the config flow
- Store the device secret key in the config entry
- Use the library callback as the authoritative source of live state
- Expose lock, battery, and device-specific Touch metrics as Home Assistant entities
- Provide explicit forced lock/unlock actions for recovery scenarios

## Supported devices

The integration targets devices compatible with the pinned `gomalock` library, including:

- Sesame 5
- Sesame 5 Pro
- Sesame Touch
- Other Sesame BLE models supported by the underlying library

## Features

- BLE discovery using `gomalock.SesameScanner.discover`
- Config flow for adding and configuring devices
- Secret-key based setup for already registered devices
- Registration support for newly added devices when applicable
- Lock entity with lock / unlock / open actions
- Battery sensor for lock devices
- Touch-specific sensors for card, fingerprint, and password counts
- Callback-driven state updates from `gomalock`
- Force lock / force unlock actions for explicit recovery
- Multi-language strings for English, Simplified Chinese, Traditional Chinese, and Japanese

## Requirements

- Home Assistant
- Python 3.12+
- Bluetooth adapter available on the host
- `gomalock==2.1.0`

## Installation

1. Copy the repository into your Home Assistant custom_components folder.
2. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Restart Home Assistant.
4. Open Settings -> Devices & Services -> Add Integration.
5. Search for `Sesame 5 BLE` and follow the config flow.

## Config flow behavior

The flow is designed as follows:

1. Discover nearby devices with `gomalock.SesameScanner.discover`
2. Show each device with:
   - Address
   - Model
   - Registered status
   - UUID
3. If the device is already registered:
   - Ask the user to enter `SECRET_KEY`

   > **Note:** For instructions on how to obtain the `SECRET_KEY`, please refer to the [gomalock](https://github.com/meronepy/gomalock) project.

4. If the device is not registered:
   - Ask whether to register it
   - If approved, call the device registration flow
   - Save the resulting `SECRET_KEY`

   > **Warning:** It is not recommended to bind unregistered devices. Since the QR code generation feature has not been implemented yet, once bound, you will not be able to share the device with other devices.

## Architecture notes

The project intentionally keeps the state path and command path separate:

- Command path: send actual lock / unlock operation to `gomalock`
- State path: listen to the gomalock callback and update Home Assistant from the callback payload
- Fallback normalization: used only when no callback payload is available and only for startup / base-state readback

This matches the real library model and avoids unnecessary BLE wakeups or stale state caused by reading partially connected device properties.

## Example: register a new device

```python
import asyncio
import gomalock

ADDRESS = "XX:XX:XX:XX:XX:XX"

async def main():
    async with gomalock.Sesame5(ADDRESS) as sesame5:
        secret_key = await sesame5.register()
        print(secret_key)

asyncio.run(main())
```

## Notes

- This custom integration is designed for Home Assistant local BLE control
- State sync relies on the gomalock callback model rather than aggressive periodic polling
- Real-world compatibility depends on the exact Sesame model and Bluetooth environment
- Testing on the target device is recommended before distribution
