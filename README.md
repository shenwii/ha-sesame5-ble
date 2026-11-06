# ha-sesame5-ble

<p align="center">
  <img src="custom_components/sesame5_ble/brand/logo.svg" alt="Sesame 5 BLE Banner" width="480">
</p>

<p align="center">
  <strong>Home Assistant custom integration for CANDY HOUSE Sesame smart locks and Touch devices via direct Bluetooth Low Energy (BLE).</strong><br>
  <em>100% Local • Ultra-Low Latency • No Hub or Cloud Required</em>
</p>

<p align="center">
  <a href="README.md"><strong>English</strong></a> •
  <a href="README_JA.md"><strong>日本語</strong></a>
</p>

<p align="center">
  <a href="https://github.com/hacs/default"><img src="https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square" alt="HACS Custom"></a>
  <a href="https://github.com/shenwii/ha-sesame5-ble/releases"><img src="https://img.shields.io/github/v/release/shenwii/ha-sesame5-ble?style=flat-square&color=blue" alt="Latest Release"></a>
  <a href="https://www.home-assistant.io"><img src="https://img.shields.io/badge/Home%20Assistant-2024.1%2B-41BDF5.svg?style=flat-square&logo=home-assistant" alt="Home Assistant 2024.1+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/shenwii/ha-sesame5-ble?style=flat-square&color=green" alt="License: MIT"></a>
</p>

---

## ✨ Features

- ⚡ **100% Local Control**: Communicates directly with Sesame devices via Bluetooth LE. No Sesame Wi-Fi Hub, CANDY HOUSE cloud account, or internet connection required.
- 🚀 **Push-Driven State Updates**: Uses the underlying [`gomalock`](https://github.com/meronepy/gomalock) push notification callback architecture rather than aggressive polling, ensuring fast status updates while preserving device battery life.
- 📱 **Broad Device Compatibility**: Supports Sesame 5, Sesame 5 Pro, Sesame 5 US, Sesame Touch / Touch Pro, and related models.
- 🔒 **Comprehensive Entity Support**:
  - Full `lock` entity controls: **Lock**, **Unlock**, and **Open** (unlatch).
  - Accurate battery levels for both Lock and Touch devices.
  - Real-time mechanical angle (`°`) position and threshold monitoring.
  - Sesame Touch statistics: registered NFC cards, fingerprints, and passcode counts.
  - Dedicated Force Lock & Force Unlock action buttons.
- 🛠️ **Custom Home Assistant Services**: Provides services for forced locking/unlocking and dynamic angle threshold configuration.
- 🌍 **Multi-Language Support**: Complete UI translations for English, Japanese (日本語), Simplified Chinese (简体中文), and Traditional Chinese (繁體中文).

---

## 📟 Supported Devices

| Device | Type | Supported Features |
| :--- | :--- | :--- |
| **Sesame 5** | Smart Lock | Lock, Unlock, Open, Battery, Angle Position, Thresholds |
| **Sesame 5 Pro** | Smart Lock | Lock, Unlock, Open, Battery, Angle Position, Thresholds |
| **Sesame 5 US** | Smart Lock | Lock, Unlock, Open, Battery, Angle Position, Thresholds |
| **Sesame Touch** | Keypad / Reader | Battery, Registered Cards, Fingerprints, Passwords |
| **Sesame Touch Pro** | Keypad / Reader | Battery, Registered Cards, Fingerprints, Passwords |
| *Other Sesame OS3 BLE devices* | Lock / Accessory | Tested against models supported by `gomalock` |

---

## 📋 Requirements

- **Home Assistant**: version `2024.1.0` or newer.
- **Bluetooth Adapter**: A functioning Bluetooth adapter on your Home Assistant host (built-in Bluetooth or USB dongle).
- **Python**: version `3.12` or newer.
- **Python Library**: [`gomalock`](https://github.com/meronepy/gomalock) (automatically installed by Home Assistant).

> [!TIP]
> USB 3.0 ports are known to emit 2.4 GHz radio frequency interference that affects Bluetooth reception. For best performance, plug your Bluetooth dongle into a USB 2.0 port or use a short USB 2.0 extension cable.

---

## 📦 Installation

### Method 1: Via HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. In Home Assistant, navigate to **HACS** → **Integrations**.
3. Click the **⋮** menu in the top right corner and choose **Custom repositories**.
4. Fill in the repository details:
   - **Repository**: `https://github.com/shenwii/ha-sesame5-ble`
   - **Type**: `Integration`
5. Click **Add**.
6. Search for **Sesame 5 BLE**, click **Download**, and confirm.
7. **Restart Home Assistant**.

### Method 2: Manual Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/shenwii/ha-sesame5-ble.git
   ```
2. Copy the `custom_components/sesame5_ble` directory into your Home Assistant's `config/custom_components/` directory:
   ```bash
   cp -r ha-sesame5-ble/custom_components/sesame5_ble /path/to/your/ha-config/custom_components/
   ```
3. Restart Home Assistant.

---

## ⚙️ Configuration & Setup

### 1. Adding the Integration

1. Go to **Settings** → **Devices & Services** → **Add Integration**.
2. Search for **Sesame 5 BLE**.
3. Home Assistant will scan for nearby Sesame devices over Bluetooth.
4. Select your device from the discovered list.

### 2. Device Registration / Secret Key

Depending on whether the device has already been paired in the official Sesame app:

#### Option A: Device Already Registered in Sesame App (Recommended)
If your lock is already registered and working in the official Sesame app:
1. Home Assistant will prompt you to enter the **`SECRET_KEY`**.
2. **How to obtain your `SECRET_KEY`**:
   - Open the official **Sesame** mobile app.
   - Tap your device → tap the **Settings** (gear) icon.
   - Choose **Share** / **Key Sharing** and generate a QR code (Owner or Manager level).
   - Scan the QR code using any QR code scanner app. The decoded URL typically looks like:
     ```text
     ssm://UI?sk=...&pk=...&l=...
     ```
   - The value after `sk=` is your device's secret key (a 16-byte hex string or base64-encoded string).
   - Alternatively, you can use the [`gomalock`](https://github.com/meronepy/gomalock) CLI tool or QR decoder utilities to inspect the key.
3. Paste the `SECRET_KEY` into Home Assistant and submit.

#### Option B: Registering an Unregistered Device
If the device has never been registered:
1. Home Assistant will ask if you want to register the device now.
2. If confirmed, Home Assistant will initialize the device registration flow and securely save the generated key.

> [!WARNING]
> We strongly recommend registering your device in the official **Sesame mobile app first**, then exporting the `SECRET_KEY` to Home Assistant. Registering a brand-new device directly inside Home Assistant will pair the lock with Home Assistant exclusively, preventing easy key sharing via the official mobile app until a QR code exporter is used.

---

## 🧩 Entities Reference

### Sesame Smart Lock Devices

| Entity | Platform | Type / Unit | Description |
| :--- | :--- | :--- | :--- |
| **Sesame Lock** | `lock` | Lock entity | Controls the lock mechanism: **Lock**, **Unlock**, and **Open** (unlatch). |
| **Lock State** | `binary_sensor` | `BinarySensorDeviceClass.LOCK` | Binary indicator for UI & automations (`on` = Unlocked, `off` = Locked). |
| **Battery** | `sensor` | Percentage (`%`) | Real-time battery percentage of the lock. |
| **Position** | `sensor` | Degrees (`°`) | Current physical angle of the lock turn mechanism. |
| **Lock Position** | `sensor` | Degrees (`°`) | Calibrated target threshold angle for the locked state. |
| **Unlock Position** | `sensor` | Degrees (`°`) | Calibrated target threshold angle for the unlocked state. |
| **Force Lock** | `button` | Button entity | Sends an unconditional lock command (bypassing state checks). |
| **Force Unlock** | `button` | Button entity | Sends an unconditional unlock command (bypassing state checks). |

### Sesame Touch / Touch Pro Devices

| Entity | Platform | Type / Unit | Description |
| :--- | :--- | :--- | :--- |
| **Battery** | `sensor` | Percentage (`%`) | Current battery level of the Sesame Touch. |
| **Cards Number** | `sensor` | Measurement | Total count of registered NFC/RFID cards. |
| **Fingerprints Number**| `sensor` | Measurement | Total count of registered fingerprints. |
| **Passwords Number** | `sensor` | Measurement | Total count of configured PIN passcodes. |

---

## 🔧 Custom Services

The integration provides custom services registered under the `sesame5_ble` domain:

### `sesame5_ble.lock`
Forces the Sesame lock into the locked position without pre-checking the current state.
```yaml
service: sesame5_ble.lock
data:
  entry_id: "your_config_entry_id" # Optional. If omitted, applies to all configured locks.
```

### `sesame5_ble.unlock`
Forces the Sesame lock into the unlocked position without pre-checking the current state.
```yaml
service: sesame5_ble.unlock
data:
  entry_id: "your_config_entry_id" # Optional. If omitted, applies to all configured locks.
```

### `sesame5_ble.set_lock_position`
Dynamically adjusts the physical lock and unlock angle thresholds.
```yaml
service: sesame5_ble.set_lock_position
data:
  entry_id: "your_config_entry_id" # Optional
  lock_position: 180               # Required (0-100/degrees)
  unlock_position: 90              # Required (0-100/degrees)
```

---

## 💡 Automation Examples

### 1. Auto-Lock Door at Bedtime
```yaml
alias: "Auto-Lock Front Door at 23:00"
trigger:
  - platform: time
    at: "23:00:00"
condition:
  - platform: state
    entity_id: lock.sesame_lock
    state: "unlocked"
action:
  - service: lock.lock
    target:
      entity_id: lock.sesame_lock
```

### 2. Low Battery Alert Notification
```yaml
alias: "Sesame Lock Low Battery Warning"
trigger:
  - platform: numeric_state
    entity_id: sensor.sesame_device_battery
    below: 20
action:
  - service: notify.notify
    data:
      title: "Smart Lock Battery Low"
      message: >
        Front door Sesame lock battery is at {{ states('sensor.sesame_device_battery') }}%. Please replace the CR123A batteries soon.
```

---

## 🏛️ Architecture & Design

```
┌────────────────────────────────────────────────────────┐
│                   Home Assistant Core                  │
│   (Lock Platform / Sensors / Binary Sensors / Buttons) │
└─────────────┬────────────────────────────▲─────────────┘
   Command    │                            │  State Updates
   (Async)    │                            │  (BLE Callbacks)
              ▼                            │
┌───────────────────────────┐    ┌───────────────────────┐
│     SesameCoordinator     │    │   SesameMechStatus    │
│    (Connection & Ready    │    │   Callback Listener   │
│         Serializers)      │    │  (Zero-Polling Push)  │
└─────────────┬─────────────┘    └─────────▲─────────────┘
              │                            │
              ▼                            │
┌────────────────────────────────────────────────────────┐
│               gomalock (Python BLE Driver)             │
│        (OS3 Protocol / Bleak / BLE Advertisements)     │
└───────────────────────────┬────────────────────────────┘
                            │ BLE GATT / Advertisements
                            ▼
           [CANDY HOUSE Sesame 5 / Touch Device]
```

- **Dual-Path Separation**:
  - **Command Path**: Commands (`lock`, `unlock`, `open`) are sent sequentially using per-device async locks to prevent BLE bus collisions.
  - **State Path**: Instead of high-frequency polling, state updates arrive directly via `gomalock`'s push notification callbacks whenever the device status changes.
- **Resource Management**: Device handles are gracefully cleaned up during integration unload or Home Assistant shutdown.

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><strong>Q: Why does Home Assistant say "No Sesame BLE devices were found nearby"?</strong></summary>

1. Ensure Bluetooth is enabled and functioning on your Home Assistant host.
2. Confirm the Sesame lock is within Bluetooth range (typically 5–10 meters without heavy concrete walls).
3. If the Sesame lock is currently actively communicating with the official mobile app, it may temporarily refuse connections from other devices. Close the mobile app and try scanning again.
4. Avoid USB 3.0 port interference by using a USB extension cable for your Bluetooth dongle.
</details>

<details>
<summary><strong>Q: Can I use Home Assistant Bluetooth Proxies (ESPHome)?</strong></summary>

Currently, active GATT connections and cryptographic handshakes with Sesame OS3 are handled directly by the host's Bluetooth stack via `Bleak`. Using a local Bluetooth adapter or USB dongle directly on the HA host is recommended.
</details>

<details>
<summary><strong>Q: How do I find my device's Config Entry ID for custom services?</strong></summary>

Go to **Settings** → **Devices & Services** → **Sesame 5 BLE** → click your device. Look at your browser URL bar: the string following `config_entries/` is the entry ID. (Alternatively, omit `entry_id` to apply to all configured locks).
</details>

---

## 🧑‍💻 Developer Reference: gomalock Direct Script

If you want to test device connectivity outside of Home Assistant using Python:

```python
import asyncio
import gomalock

ADDRESS = "XX:XX:XX:XX:XX:XX"  # Replace with device MAC address
SECRET_KEY = "your_hex_secret_key"

async def main():
    async with gomalock.Sesame5(ADDRESS, secret_key=SECRET_KEY) as lock:
        await lock.connect()
        await lock.login()
        print("Battery:", lock.mech_status.battery_percentage)
        print("Locked:", lock.mech_status.is_in_lock_range)
        # To unlock: await lock.unlock("script")
        # To lock: await lock.lock("script")

asyncio.run(main())
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgements

- [CANDY HOUSE](https://jp.candyhouse.co/) for developing the Sesame smart lock series.
- [@meronepy](https://github.com/meronepy) for the outstanding [`gomalock`](https://github.com/meronepy/gomalock) library that makes BLE local communication possible.
