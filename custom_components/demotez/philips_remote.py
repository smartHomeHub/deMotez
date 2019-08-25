import logging
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .base_remote import Remote

_LOGGER = logging.getLogger(__name__)

class PhilipsRemote(Remote):
    async def event_received(self, event_id):
        if event_id == 1002:
            await self.turn_on_off('turn_on')

        if event_id == 4002:
            await self.turn_on_off('turn_off')

        if event_id == 1001:
            await self.turn_on_off('turn_on', True)

        if event_id == 4001:
            await self.turn_on_off('turn_off', True)

        if event_id in [2002, 3002]:
            await self.short_dimming(event_id)

        if event_id in [2001, 3001]:
            await self.long_dimming(event_id)

    async def turn_on_off(self, action, long = False):
        config = self.remote_config.get(
            'long_' + action if long is True else action
        )
        transition = config.get('transition')
        entities = config.get('entities')

        for entity_id in entities:
            service_data = {'entity_id': entity_id}

            if transition:
                service_data['transition'] = transition

            await self.hass.services.async_call('homeassistant', action, service_data)

    async def long_dimming(self, event_id):
        dimming_config = self.remote_config.get('dimming')
        step = dimming_config.get('step')
        transition = dimming_config.get('transition')
        long_press_full_brightness = dimming_config.get('long_press_full_brightness')
        long_press_turn_off = dimming_config.get('long_press_turn_off')
        entities = dimming_config.get('entities')
        min_brightness = 1
        max_brightness = 255

        if event_id == 2001:
            for entity_id in entities:
                if long_press_full_brightness:
                    brightness = max_brightness
                else:
                    brightness = self.hass.states.get(entity_id).attributes.get('brightness')

                    if brightness:
                        brightness += step

                        if brightness > max_brightness: 
                            brightness = max_brightness

                await self.set_brightness(entity_id, brightness, transition)

        if event_id == 3001:
            for entity_id in entities:
                if long_press_turn_off:
                    brightness = 0
                else:
                    brightness = self.hass.states.get(entity_id).attributes.get('brightness')

                    if brightness:
                        brightness -= step

                        if brightness < min_brightness: 
                            brightness = min_brightness

                await self.set_brightness(entity_id, brightness, transition)