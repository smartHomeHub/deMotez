import asyncio
import logging
import time
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .base_remote import Remote

_LOGGER = logging.getLogger(__name__)

class TradfriSwitch(Remote):
    async def event_received(self, event_id):
        if event_id == 1002:
            await self.turn_on_off('turn_on')

        if event_id == 2002:
            await self.turn_on_off('turn_off')

        if event_id in [1001, 2001]:
            await self.long_dimming(event_id)

        if event_id in [1003, 2003]:
            self._long_dim_released = True

    async def turn_on_off(self, action):
        config = self.remote_config.get(action)
        transition = config.get('transition')
        entities = config.get('entities')

        for entity_id in entities:
            service_data = {'entity_id': entity_id}

            if transition:
                service_data['transition'] = transition

            await self.hass.services.async_call('homeassistant', action, service_data)

    async def long_dimming(self, event_id):
        dimming_config = self.remote_config.get('dimming')
        step = 30
        entities = dimming_config.get('entities')
        min_brightness = 1
        max_brightness = 255

        if event_id == 1001:
            self._long_dim_released = False

            while self._long_dim_released == False:
                max_bright = dict.fromkeys(entities, False)

                for entity_id in entities:
                    brightness = self.hass.states.get(entity_id).attributes.get('brightness')
                    
                    if brightness:
                        brightness += step

                        if brightness > max_brightness: 
                            brightness = max_brightness
                            max_bright[entity_id] = True

                    await self.set_brightness(entity_id, brightness, None)
                    await asyncio.sleep(0.1)

                    if all(x is True for x in max_bright.values()):
                        self._long_dim_released = True

        if event_id == 2001:
            self._long_dim_released = False

            while self._long_dim_released == False:
                max_bright = dict.fromkeys(entities, False)

                for entity_id in entities:                  
                    brightness = self.hass.states.get(entity_id).attributes.get('brightness')
                    
                    if brightness:
                        brightness -= step

                        if brightness < min_brightness: 
                            brightness = min_brightness
                            max_bright[entity_id] = True

                    await self.set_brightness(entity_id, brightness, None)
                    await asyncio.sleep(0.1)

                    if all(x is True for x in max_bright.values()):
                        self._long_dim_released = True