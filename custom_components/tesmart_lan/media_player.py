import logging
import socket
import time
from json import dumps, loads  # Add this import

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.media_player import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    MediaPlayerEntity,
)
from homeassistant.components.media_player.const import MediaPlayerEntityFeature
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_FRIENDLY_NAME,
    STATE_ON,
)
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.reload import async_setup_reload_service

_LOGGER = logging.getLogger(__name__)

DOMAIN = "tesmart_lan"  # Define the domain
PLATFORMS = ["media_player"]

CONF_LAN = "lans"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SOURCES = "sources"
CONF_UNIQUE_ID = "unique_id"
CONF_SOURCE_IGNORE = "source_ignore"

SOURCES = {f"HDMI {i}": f"HDMI {i}" for i in range(1, 17)}

LAN_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=5000): cv.positive_int,
        vol.Optional(CONF_SOURCES): cv.ensure_list,
        vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
        vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_SOURCE_IGNORE, default=[]): vol.All(
            cv.ensure_list, [cv.string]
        ),
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_LAN): cv.schema_with_slug_keys(LAN_SCHEMA)}
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the template binary sensors."""
    await async_setup_reload_service(hass, DOMAIN, PLATFORMS)
    async_add_entities(await _async_create_entities(hass, config))


async def _async_create_entities(hass, config):
    """Set up the Template switch."""
    lans = []

    for device, device_config in config[CONF_LAN].items():
        friendly_name = device_config.get(ATTR_FRIENDLY_NAME, device)
        unique_id = device_config.get(CONF_UNIQUE_ID)
        host = device_config.get(CONF_HOST)
        port = device_config.get(CONF_PORT)
        sources = device_config.get(CONF_SOURCES)

        lans.append(
            TesmartLan(hass, device, friendly_name, unique_id, host, port, sources)
        )
    return lans


class TesmartLan(MediaPlayerEntity):
    """Representation of a Template Media player."""

    def __init__(self, hass, device_id, friendly_name, unique_id, host, port, sources):
        """Initialize the Template Media player."""
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
        if sources is not None and sources != {}:
            self._source_list = loads(dumps(sources).strip("[]"))
        else:
            self._source_list = SOURCES.copy()

        self._source_ignore = []  # Initialize _source_ignore as an empty list
        if sources is not None and CONF_SOURCE_IGNORE in sources:
            self._source_ignore = sources[CONF_SOURCE_IGNORE]

        self.active_port = None  # Initialize active_port attribute
        self._sound_mode = None
        self._last_selected_source = None  # Initialize last selected source attribute

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def device_class(self):
        """Return the class of this device."""
        return "tv"

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
        support |= MediaPlayerEntityFeature.SELECT_SOURCE
        support |= MediaPlayerEntityFeature.SELECT_SOUND_MODE
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
    def sound_mode(self):
        """Return the current sound mode."""
        return self._sound_mode

    @property
    def sound_mode_list(self):
        """Return the available sound modes."""
        return ["Beeper On", "Beeper Off"]  # Update with actual sound modes

    @property
    def source(self):
        """Return the current input source."""
        if self.active_port is not None:
            return self.active_port

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            data = bytes.fromhex("AABB031000EE")
            s.send(data)
            time.sleep(0.2)
            self.active_port = self.sources[s.recv(6)[5] - 1]
        except Exception:
            pass

        return self.active_port

    @property
    def source_list(self):
        """Return the list of available input sources."""
        source_list = self._source_list.copy()
        for source_ignore in self._source_ignore:
            if source_ignore in source_list:
                del source_list[source_ignore]

        if len(source_list) > 0:
            return list(source_list.values())
        else:
            return None

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    async def async_select_source(self, source):
        """Set the input source."""
        self.active_port = source
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            data = bytes.fromhex(f"AABB0301{int(self.sources.index(source) + 1):02x}EE")
            s.send(data)
        except Exception:
            pass
        self.async_schedule_update_ha_state()

    async def async_select_sound_mode(self, sound_mode):
        """Set the sound mode."""
        packet = "01" if sound_mode == "Beeper On" else "00"

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            data = bytes.fromhex(f"AABB0302{packet}EE")
            s.send(data)
        except Exception:
            pass

        self._sound_mode = sound_mode
        self.async_schedule_update_ha_state()

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        # Retrieve the last selected source from the entity registry
        if self.entity_id in self.hass.data:
            self._last_selected_source = self.hass.data[self.entity_id].get(
                "last_selected_source"
            )

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # Store the last selected source in the entity registry
        if self.entity_id not in self.hass.data:
            self.hass.data[self.entity_id] = {}
        self.hass.data[self.entity_id]["last_selected_source"] = (
            self._last_selected_source
        )
        await super().async_will_remove_from_hass()
