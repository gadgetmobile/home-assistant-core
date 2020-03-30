"""Config flow for BleBox devices integration."""
import logging

from blebox_uniapi.error import Error, UnsupportedBoxVersion
from blebox_uniapi.products import Products
from blebox_uniapi.session import ApiHost
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .errors import CannotConnect, UnsupportedVersion

DEFAULT_HOST = "192.168.0.2"
DEFAULT_PORT = 80

_LOGGER = logging.getLogger(__name__)


def host_port(data):
    """Return a list with host and port."""
    return (data[CONF_HOST], data[CONF_PORT])


def create_schema(previous_input=None):
    """Create a schema with given values as default."""
    if previous_input is not None:
        host, port = host_port(previous_input)
    else:
        host = DEFAULT_HOST
        port = DEFAULT_PORT

    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=host): str,
            vol.Required(CONF_PORT, default=port): int,
        }
    )


class BleBoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BleBox devices."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the BleBox config flow."""
        self.device_config = {}

    async def async_step_user(self, user_input=None):
        """Handle initial user-triggered config step."""

        errors = {}
        if user_input is not None:

            addr = host_port(user_input)
            address = "{0}:{1}".format(*addr)

            for entry in self.hass.config_entries.async_entries(DOMAIN):
                if addr == host_port(entry.data):
                    return self.async_abort(
                        reason="address_already_configured",
                        description_placeholders={"address": address},
                    )

            try:
                hass = self.hass
                websession = async_get_clientsession(hass)
                api_host = ApiHost(*addr, None, websession, hass.loop, _LOGGER)

                try:
                    product = await Products.async_from_host(api_host)

                except UnsupportedBoxVersion as ex:
                    _LOGGER.error("Outdated device firmware at %s:%d (%s)", *addr, ex)
                    raise UnsupportedVersion from ex

                except Error as ex:
                    _LOGGER.error("Failed to identify device at %s:%d (%s)", *addr, ex)
                    raise CannotConnect from ex

                # Check if configured but IP changed since
                mac_address = product.unique_id
                await self.async_set_unique_id(mac_address)
                self._abort_if_unique_id_configured()

                # Return some info we want to store in the config entry.
                info = {"title": product.name}

                return self.async_create_entry(title=info["title"], data=user_input)
            except UnsupportedVersion:
                errors["base"] = "unsupported_version"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except RuntimeError as ex:
                _LOGGER.exception("Unexpected exception: %s", ex)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=create_schema(user_input),
            errors=errors,
            description_placeholders={"address": addr},
        )
