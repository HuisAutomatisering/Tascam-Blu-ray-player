# Tascam BD-MP4K Blu-ray player

Place the folder tascam_bdmp4k in custom_components/ directory within your Home Assistant configuration directory. After that, restart Home Assistant, and it should load the custom integration.

markdown
# TASCAM BD-MP4K Blu-ray Player Integration for Home Assistant

This integration allows you to control your TASCAM BD-MP4K Blu-ray player from Home Assistant.

## Installation

1. Copy the `tascam_bd_mp4k` directory to your Home Assistant `custom_components` directory and reboot.

2. Add the integration via with config flow.

Search for the Tascam integration and add ip-adres of your TASCAM BD-MP4K Blu-ray player.


Supported Features

    Div. sensors and buttons
    Mediaplayer With Play, Pause, next and previous.

Usage

Once the integration is set up, you can control your TASCAM BD-MP4K Blu-ray player using the Home Assistant UI or through automations and scripts.

Configuration Options

    host: (string) The IP address of the TASCAM BD-MP4K Blu-ray player.
    port: (integer) The port number for communication with the Blu-ray player (default is 9030).

Support

For help or support, please open an issue on GitHub.
