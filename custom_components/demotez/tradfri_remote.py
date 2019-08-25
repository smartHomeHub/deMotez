import asyncio
import logging
import time
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .base_remote import Remote

_LOGGER = logging.getLogger(__name__)

class TradfriRemote(Remote):
    async def event_received(self, event_id):
        if event_id == 1002:
            await self.toggle()

        if event_id in [2002, 3002]:
            await self.short_dimming(event_id)

        if event_id in [2001, 3001]:
            await self.long_dimming(event_id)

        if event_id in [2003, 3003]:
            self._long_dim_released = True

    async def toggle(self):
        toggle_config = self.remote_config.get('toggle')
        sync_lights = toggle_config.get('sync_lights')
        transition = toggle_config.get('transition')
        entities = toggle_config.get('entities')
        action = 'toggle'

        if sync_lights is True:
            action = 'turn_off' if self.is_any_on(entities) else 'turn_on'

        for entity_id in entities:
            service_data = {'entity_id': entity_id}

            if transition:
                service_data['transition'] = transition

            await self.hass.services.async_call('homeassistant', action, service_data)

    async def long_dimming(self, event_id):
        dimming_config = self.remote_config.get('dimming')
        step = 30
        transition = dimming_config.get('transition')
        long_press_full_brightness = dimming_config.get('long_press_full_brightness')
        long_press_turn_off = dimming_config.get('long_press_turn_off')
        entities = dimming_config.get('entities')
        min_brightness = 1
        max_brightness = 255
        
        if long_press_full_brightness and event_id == 2001:
            for entity_id in entities:
                await self.set_brightness(entity_id, max_brightness, transition)
            return

        if long_press_turn_off and event_id == 3001:
            for entity_id in entities:
                await self.set_brightness(entity_id, 0, transition)
            return

        if event_id == 2001:
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

        if event_id == 3001:
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