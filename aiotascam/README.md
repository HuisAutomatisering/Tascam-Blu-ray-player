# aiotascam

Async Python client for the **Tascam BD-MP4K** Blu-ray player, implementing the
TASCAM RS-232C/Ethernet protocol over TCP (port 9030).

## Usage

```python
import asyncio
from aiotascam import TascamPlayer


async def main() -> None:
    player = TascamPlayer("192.168.1.50")
    await player.connect()
    state = await player.get_state()
    print(state)
    await player.play()
    await player.disconnect()


asyncio.run(main())
```

## Notes

- The player accepts **one** TCP client at a time; keep a single persistent
  connection.
- Power-on over Ethernet is not supported by the protocol (use Wake-on-LAN);
  `power_off()` puts the player in standby.
- In standby the player does not reply to status requests; `get_power()`
  detects this via a timeout.

## License

MIT
