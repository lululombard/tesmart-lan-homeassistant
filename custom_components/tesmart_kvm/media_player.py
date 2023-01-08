"""Support for switches which integrates with other components."""
import logging
import socket

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.components.media_player import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    MediaPlayerEntity,
)
from homeassistant.components.media_player.const import (
    SUPPORT_SELECT_SOURCE,
)
from homeassistant.components.template.const import (
    DOMAIN,
    PLATFORMS,
)
from homeassistant.components.template.template_entity import TemplateEntity
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_FRIENDLY_NAME,
    STATE_IDLE,
    STATE_OFF,
    STATE_ON,
    STATE_PAUSED,
    STATE_PLAYING,
)
from homeassistant.core import callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.helpers.script import Script

# from . import extract_entities, initialise_templates


_LOGGER = logging.getLogger(__name__)
_VALID_STATES = [
    STATE_ON,
    STATE_OFF,
    "true",
    "false",
    STATE_IDLE,
    STATE_PAUSED,
    STATE_PLAYING,
]
CONF_MEDIAPLAYER = "media_players"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SOURCES = "sources"
CONF_UNIQUE_ID = "unique_id"


MEDIA_PLAYER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=5000): cv.positive_int,
        vol.Optional(CONF_SOURCES, default=['HDMI {}'.format(i) for i in range(0, 8)]): [cv.string],
        vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
        vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_MEDIAPLAYER): cv.schema_with_slug_keys(MEDIA_PLAYER_SCHEMA)}
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the template binary sensors."""

    await async_setup_reload_service(hass, DOMAIN, PLATFORMS)
    async_add_entities(await _async_create_entities(hass, config))


async def _async_create_entities(hass, config):
    """Set up the Template switch."""
    media_players = []

    for device, device_config in config[CONF_MEDIAPLAYER].items():
        friendly_name = device_config.get(ATTR_FRIENDLY_NAME, device)
        unique_id = device_config.get(CONF_UNIQUE_ID)
        host = device_config.get(CONF_HOST)
        port = device_config.get(CONF_PORT)
        sources = device_config.get(CONF_SOURCES)

        media_players.append(
            TesmartKvm(
                hass,
                device,
                friendly_name,
                unique_id,
                host,
                port,
                sources
            )
        )
    return media_players


class TesmartKvm(TemplateEntity, MediaPlayerEntity):
    """Representation of a Template Media player."""

    def __init__(
        self,
        hass,
        device_id,
        friendly_name,
        unique_id,
        host,
        port,
        sources
    ):
        """Initialize the Template Media player."""
        super().__init__(
            hass,
        )
        self.hass = hass
        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, device_id, hass=hass
        )
        self._name = friendly_name
        self._domain = __name__.split(".")[-2]

        self._unique_id = None
        if unique_id is not None:
            self._unique_id = unique_id

        self.host = host
        self.port = port
        self.sources = sources

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def device_class(self):
        """Return the class of this device."""
        return "receiver"

    @property
    def is_on(self):
        """Return true if device is on."""
        return True

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def supported_features(self):
        """Flag media player features that are supported."""

        support = 0

        support |= SUPPORT_SELECT_SOURCE

        return support

    @property
    def available(self) -> bool:
        """Return if the device is available."""
        return True


    @property
    def state(self):
        """Return the state of the player."""
        return STATE_ON

    @property
    def source(self):
        """Return the current input source."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((self.host, self.port))

        data = bytes.fromhex("AABB030100EE")
        s.send(data)
        source = s.recv(4)
        print(source)
        return source

    @property
    def source_list(self):
        """List of available input sources."""
        return self._source_list

    @property
    def unique_id(self):
        """Unique id."""
        return self._unique_id

    async def async_select_source(self, source):
        """Set the input source."""
        # TODO
        print(source)
        print(self.sources)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        data = bytes.fromhex(f"AABB0301{int(source):02x}EE")
        s.send(data)
