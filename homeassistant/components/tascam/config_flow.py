"""Config flow for the Tascam integration."""

from __future__ import annotations

import logging
from typing import Any

from aiotascam import DEFAULT_PORT, TascamConnectionError, TascamPlayer
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import DOMAIN, MODEL_BD_MP4K

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


class TascamConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tascam."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
            player = TascamPlayer(user_input[CONF_HOST], user_input[CONF_PORT])
            try:
                await player.connect()
            except TascamConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await player.disconnect()
                return self.async_create_entry(
                    title=f"Tascam {MODEL_BD_MP4K}", data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
