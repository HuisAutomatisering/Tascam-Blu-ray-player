# Tascam BD-MP4K – Home Assistant integration

Control a Tascam BD-MP4K professional Blu-ray player over its Ethernet
control protocol (TCP port 9030) from Home Assistant.

## Features

- **Media player** entity: play, pause, stop, next/previous chapter,
  standby, media position and duration (derived from elapsed + remaining time).
- **Sensors**: disc status, playback status, elapsed time, remaining time,
  current chapter, current title.
- **Buttons**: tray open/close, home, enter, return, top menu, popup menu,
  setup menu, display info, next subtitle, mute on/off, power off.

## Architecture notes

The BD-MP4K protocol specification requires that the TCP connection is
**held open continuously** and that **only one client** connects at a time.
This integration therefore maintains a single shared connection for all
entities, enforces the 30 ms minimum command interval, and handles the
`ack`/`nack` protocol including unsolicited status notifications.

Elapsed/remaining time and chapter/title are only queried while playing or
paused; the player replies `nack` (or `UNKN`) to these requests in other
modes, which is shown as *unknown* in Home Assistant.

## Limitations

- **Power on over Ethernet is not supported by the protocol.** Use
  Wake-on-LAN (enable WoL on the player) or RS-232C for power-on.
- Only one controller can be connected to the player at a time. Disconnect
  other control systems (e.g. Companion, Crestron) while using this
  integration.

## Installation

### HACS (roadmap is to become official)

1. Add this repository as a custom repository in HACS (category: Integration).
2. Install **Tascam BD-MP4K** and restart Home Assistant.

### Manual

1. Copy `custom_components/tascam_bdmp4k` into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.

### Configuration

Go to **Settings → Devices & Services → Add Integration**, search for
**Tascam BD-MP4K** and enter the IP address of the player. The port is
9030 and fixed by the device.

## Development

```bash
ruff check custom_components
ruff format custom_components
```

## License

MIT [LICENSE](LICENSE).

The protocol documentation is © TEAC Corporation.
