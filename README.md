# ha-sesame5-ble

![Sesame 5 BLE banner](custom_components/sesame5_ble/brand/logo.svg)

Home Assistant custom integration for CANDY HOUSE Sesame smart locks and Touch devices via Bluetooth Low Energy (BLE). Fully local — no hub or cloud account required.

## Supported Devices

- Sesame 5
- Sesame 5 Pro
- Sesame Touch
- Other Sesame BLE models supported by the underlying library

## Requirements

- Home Assistant
- A working Bluetooth adapter (built-in or USB dongle)
- Python 3.12+

## Installation

### Using HACS (Recommended)
1. From HACS, add the repository to your Home Assistant instance:
   - Open HACS → **Integrations** → **⋮** (menu) → **Custom repositories**
   - Paste `https://github.com/shenwii/ha-sesame5-ble` and select **Integration**
   - Search for **Sesame 5 BLE** and install
   - Restart Home Assistant

### Manual Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/shenwii/ha-sesame5-ble.git
   ```
2. Move the `custom_components/sesame5_ble` folder to your Home Assistant configuration directory:
   ```bash
   cp -r ha-sesame5-ble/custom_components/sesame5_ble /path/to/your/ha-config/custom_components/
   ```
3. Restart Home Assistant

## Setup

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Sesame 5 BLE**
3. Home Assistant will scan for nearby Sesame devices.
4. Select your lock or touch from the list.
5. If the device is already registered:
   - Ask the user to enter `SECRET_KEY`

   > **Note:** For instructions on how to obtain the `SECRET_KEY`, please refer to the [gomalock](https://github.com/meronepy/gomalock) project.

6. If the device is not registered:
   - Ask whether to register it
   - If approved, call the device registration flow
   - Save the resulting `SECRET_KEY`

   > **Warning:** It is not recommended to bind unregistered devices. Since the QR code generation feature has not been implemented yet, once bound, you will not be able to share the device with other devices.

## Entities

| Entity | Description |
| --- | --- |
| `SesameForceLockButton` | Button to send a force lock command to the device |
| `SesameForceUnlockButton` | Button to send a force unlock command to the device |
| `SesameLockEntity` | Main lock entity for controlling and monitoring lock status (Lock platform) |
| `SesameLockStateBinarySensor` | Binary sensor indicating the current state of the lock |
| `SesameBatterySensor` | Sensor monitoring the battery level of the lock |
| `SesameLockPositionSensor` | Sensor indicating the current position of the lock mechanism |
| `SesameLockThresholdSensor` | Sensor indicating the lock threshold configuration |
| `SesameUnlockThresholdSensor` | Sensor indicating the unlock threshold configuration |
| `SesameTouchBatterySensor` | Sensor monitoring the battery level of the Touch device |
| `SesameTouchCardCountSensor` | Sensor indicating the number of paired NFC cards |
| `SesameTouchFingerprintCountSensor` | Sensor indicating the number of registered fingerprints |
| `SesameTouchPasswordCountSensor` | Sensor indicating the number of configured passwords |

## How It Works

please refer to the [gomalock](https://github.com/meronepy/gomalock) project.

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

## Installation

1. Copy the repository into your Home Assistant custom_components folder.
2. Install the Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Restart Home Assistant.
4. Open Settings → **Devices & Services** → **Add Integration**
5. Search for `Sesame 5 BLE` and follow the config flow.

## Architecture Notes

The project intentionally keeps the state path and command path separate:

- Command Path: Send actual lock/unlock operations to `gomalock`
- State Path: Listen to the `gomalock` callback and update Home Assistant from the callback payload
- Fallback Normalization: Used only when no callback payload is available and only for startup/base-state readback

This matches the real library model and avoids unnecessary BLE wakeups or stale state caused by reading partially connected device properties.

## Example: Register a New Device

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

- This custom integration is designed for Home Assistant local BLE control.
- State synchronization relies on the `gomalock` callback model rather than aggressive periodic polling.
- Real-world compatibility depends on the exact Sesame model and Bluetooth environment.
