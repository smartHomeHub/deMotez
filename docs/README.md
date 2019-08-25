This custom integration attempts to simplify the use of Tradfri and Philips HUE remotes through deCONZ and Home Assistant. There is no more need for extensive and complex automations and it also supports long dimming that is almost impossible with HA automations.

```yaml
demotez:
  remotes:
    - type: tradfri_remote
      id: master_bedroom_remote_control
      toggle:
        sync_lights: True
        entities:
          - light.office_ceiling_light_1
          - light.office_ceiling_light_2
      dimming:
        step: 60
        long_press_full_brightness: True
        long_press_turn_off: True
        entities:
          - light.office_desk_lamp_1
          - light.office_desk_lamp_2

    - type: tradfri_dimmer
      id: tradfri_wireless_dimmer
      dimming:
        step: 60
        entities:
          - light.office_desk_lamp_1
          - light.office_desk_lamp_2
          
    - type: philips_remote
      id: dimmer_switch
      turn_on:
        entities:
          - light.office_ceiling_light_1
      turn_off:
        entities:
          - light.office_ceiling_light_1
          - light.office_ceiling_light_2
      long_turn_on:
        entities:
          - light.office_ceiling_light_1
          - light.office_ceiling_light_2
      long_turn_off:
        entities:
          - light.office_ceiling_light_1
          - light.office_ceiling_light_2
          - media_player.office_tv
          - climate.office_ac
      dimming:
        step: 60
        long_press_full_brightness: False
        long_press_turn_off: True
        entities:
          - light.office_desk_lamp_1
          - light.office_desk_lamp_2
```
