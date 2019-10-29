import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import *
from .tradfri_remote import TradfriRemote
from .tradfri_dimmer import TradfriDimmer
from .tradfri_switch import TradfriSwitch
from .philips_remote import PhilipsRemote

_LOGGER = logging.getLogger(__name__)

REMOTE_TYPES = [
    TRADFRI_REMOTE,
    TRADFRI_DIMMER,
    TRADFRI_SWITCH,
    PHILIPS_REMOTE
]

# Tradfri remotes
REMOTE_TOGGLE_SCHEMA = vol.Schema({
    vol.Optional('sync_lights', default=True): cv.boolean,
    vol.Optional('transition'): cv.positive_int,
    vol.Required('entities'): cv.entity_ids
})

# Tradfri dimmers, Tradfri switches, Philips remotes
REMOTE_TURN_ON_SCHEMA =  vol.Schema({
    vol.Optional('transition'): cv.positive_int,
    vol.Required('entities'): cv.entity_ids
})

# Tradfri dimmers, Tradfri switches, Philips remotes
REMOTE_TURN_OFF_SCHEMA =  vol.Schema({
    vol.Optional('transition'): cv.positive_int,
    vol.Required('entities'): cv.entity_ids
})

# Philips remotes
REMOTE_LONG_TURN_ON_SCHEMA =  vol.Schema({
    vol.Optional('transition'): cv.positive_int,
    vol.Required('entities'): cv.entity_ids
})

# Philips remotes
REMOTE_LONG_TURN_OFF_SCHEMA =  vol.Schema({
    vol.Optional('transition'): cv.positive_int,
    vol.Required('entities'): cv.entity_ids
})

# Tradfri remotes, Trandfi dimmers, Tradfri switches, Philips remotes
REMOTE_DIMMING_SCHEMA = vol.Schema({
    vol.Optional('step', default=30): cv.positive_int,
    vol.Optional('transition'): cv.positive_int,
    vol.Optional('long_press_full_brightness', default=False): cv.boolean,
    vol.Optional('long_press_turn_off', default=False): cv.boolean,
    vol.Required('entities'): cv.entity_ids
})

REMOTE_SCHEMA = vol.Schema({
    vol.Required('type'): vol.In(REMOTE_TYPES),
    vol.Required('id'): cv.string,
    vol.Optional('toggle'): REMOTE_TOGGLE_SCHEMA,
    vol.Optional('turn_on'): REMOTE_TURN_ON_SCHEMA,
    vol.Optional('turn_off'): REMOTE_TURN_OFF_SCHEMA,
    vol.Optional('long_turn_on'): REMOTE_LONG_TURN_ON_SCHEMA,
    vol.Optional('long_turn_off'): REMOTE_LONG_TURN_OFF_SCHEMA,
    vol.Optional('dimming'): REMOTE_DIMMING_SCHEMA
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required('remotes'): vol.All(cv.ensure_list, [REMOTE_SCHEMA])
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    conf = config.get(DOMAIN)
    remotes = []

    for remote_config in conf.get('remotes'):
        remote_type = remote_config.get('type')

        if remote_type == TRADFRI_REMOTE:
            remotes.append(TradfriRemote(hass, remote_config))

        if remote_type == TRADFRI_DIMMER:
            remotes.append(TradfriDimmer(hass, remote_config))

        if remote_type == TRADFRI_SWITCH:
            remotes.append(TradfriSwitch(hass, remote_config))
        
        if remote_type == PHILIPS_REMOTE:
            remotes.append(PhilipsRemote(hass, remote_config))

    async def dispatch_deconz_events(event):
        async_dispatcher_send(hass, DECONZ_EVENT, event)

    hass.bus.async_listen(DECONZ_EVENT, dispatch_deconz_events)

    return True