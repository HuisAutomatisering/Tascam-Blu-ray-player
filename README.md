# Tascam-Blu-ray-player

Place in custom_components/tascam_bd_mp4k directory within your Home Assistant configuration directory. After that, restart Home Assistant, and it should load the custom integration.

markdown
# TASCAM BD-MP4K Blu-ray Player Integration for Home Assistant

This integration allows you to control your TASCAM BD-MP4K Blu-ray player from Home Assistant.

## Installation

1. Copy the `tascam_bd_mp4k` directory to your Home Assistant `custom_components` directory.

2. Add the following configuration to your `configuration.yaml` file:

yaml
```
media_player:
  - platform: tascam_bd_mp4k
    host: YOUR_MEDIA_PLAYER_IP_ADDRESS
    port: 9030
```

Replace YOUR_MEDIA_PLAYER_IP_ADDRESS with the IP address of your TASCAM BD-MP4K Blu-ray player.

    Restart Home Assistant to load the new integration.

Supported Features

    Power on/off
    Play
    Pause

Usage

Once the integration is set up, you can control your TASCAM BD-MP4K Blu-ray player using the Home Assistant UI or through automations and scripts.
Example Automation

yaml
```
automation:
  - alias: "Play Movie"
    trigger:
      platform: state
      entity_id: input_boolean.play_movie
      to: "on"
    action:
      service: media_player.media_play
      target:
        entity_id: media_player.tascam_media_player
```

Example Script

yaml
```
script:
  play_movie:
    sequence:
      - service: media_player.media_play
        target:
          entity_id: media_player.tascam_media_player
```

Configuration Options

    host: (string) The IP address of the TASCAM BD-MP4K Blu-ray player.
    port: (integer) The port number for communication with the Blu-ray player (default is 9030).

Support

For help or support, please open an issue on GitHub.
