import asyncio
import logging
import time

from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DECONZ_EVENT

_LOGGER = logging.getLogger(__name__)

class Remote:
    def __init__(self, hass, remote_config):
        self.hass = hass
        self.remote_config = remote_config

        async_dispatcher_connect(
            self.hass, DECONZ_EVENT, self.handle_events)

    async def handle_events(self, event):
        device_id = event.data.get('id')
        event_id = event.data.get('event')

        if not device_id == self.remote_config.get('id'):
            return

        await self.event_received(event_id)
   
    async def event_received(self, event_id):
        raise NotImplementedError()

    async def short_dimming(self, event_id):
        dimming_config = self.remote_config.get('dimming')
        step = dimming_config.get('step')
        transition = dimming_config.get('transition')
        entities = dimming_config.get('entities')
        min_brightness = 1
        max_brightness = 255

        for entity_id in entities:
            brightness = self.hass.states.get(entity_id).attributes.get('brightness')

            # If the brightness is none (light turned off?), turn on the light
            if brightness and event_id == 2002:
                brightness += step

                if brightness > max_brightness: 
                    brightness = max_brightness

            if brightness and event_id == 3002:
                brightness -= step

                if brightness < min_brightness: 
                    brightness = min_brightness

            await self.set_brightness(entity_id, brightness, transition)

    async def set_brightness(self, entity_id, brightness, transition):
        service_data = {'entity_id': entity_id}

        if not brightness is None:
            service_data['brightness'] = brightness

        if not transition is None:
            service_data['transition'] = transition

        await self.hass.services.async_call('light', 'turn_on', service_data)
    
    def is_any_on(self, entities):
        for entity_id in entities:
            if self.hass.states.get(entity_id).state == 'on':
                return True