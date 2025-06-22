from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_PORT, DEFAULT_PORT

class TascamBDMP4KConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Tascam BD-MP4K", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            })
        )
