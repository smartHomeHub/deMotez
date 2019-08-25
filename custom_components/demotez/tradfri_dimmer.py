import logging
from datetime import timedelta
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import Throttle
from .base_remote import Remote

_LOGGER = logging.getLogger(__name__)

class TradfriDimmer(Remote):
    @Throttle(timedelta(seconds=0.5))
    async def event_received(self, event_id):
        if event_id == 4002:
            await self.turn_off()

        if event_id in [2002, 3002]:
            await self.short_dimming(event_id)

    async def turn_off(self):
        config = self.remote_config.get('dimming')
        transition = config.get('transition')
        entities = config.get('entities')

        for entity_id in entities:
            service_data = {'entity_id': entity_id}

            if transition:
                service_data['transition'] = transition

            await self.hass.services.async_call('light', 'turn_off', service_data)