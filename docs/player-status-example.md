# Current player status: health, prayer, spec, run energy, online/world and aggression timer

This example is the green part of the image below, it works well on desktop as well as mobile

<img src="images/skill_status.jpg" alt="Prayer Tile Example" width="300px">

## HACS used in the example

- lovelace button-card: https://github.com/custom-cards/button-card

## Example

Create a manual card with the following yaml content:

```yaml
type: grid
columns: 1
square: false
cards:
  - type: custom:button-card
    entity: sensor.runelite_%username%_health
    show_state: false
    show_name: false
    show_icon: false
    styles:
      custom_fields:
        info:
          - display: flex
          - flex-direction: row
          - align-items: center
          - justify-content: space-between
          - width: 100%
          - height: 100%
      card:
        - background-color: "#1e1e1e"
        - border-radius: 10px
        - height: 40px
        - width: 80px
        - padding: 6px 6px
        - position: relative
    custom_fields:
      info: |
        [[[
          const runenergy = entity.attributes.current_health ?? 'N/A';
          return `
            <div style="display: flex; align-items: center; width: 100;">
              <div style="text-align:left;background-color: #685A4B; color: white; font-size: 12px; padding: 2px 3px ; font-weight: bold;  border-radius: 3px; text-shadow: 0px 0px 3px black; width: 35px; border: 1px solid #4C4338">
                ${runenergy}
              </div>
              <img src="https://oldschool.runescape.wiki/images/Hitpoints_orb.png?35952" style="width: 26px; height: 26px; margin-left: -5px" />
            </div>
          `;
        ]]]
  - type: custom:button-card
    entity: sensor.runelite_%username%_prayer
    show_state: false
    show_name: false
    show_icon: false
    styles:
      custom_fields:
        info:
          - display: flex
          - flex-direction: row
          - align-items: center
          - justify-content: space-between
          - width: 100%
          - height: 100%
      card:
        - background-color: "#1e1e1e"
        - border-radius: 10px
        - height: 40px
        - width: 80px
        - padding: 6px 6px
        - position: relative
    custom_fields:
      info: |
        [[[
          const runenergy = entity.attributes.current_prayer ?? 'N/A';
          return `
            <div style="display: flex; align-items: center; width: 100;">
              <div style="text-align:left;background-color: #685A4B; color: white; font-size: 12px; padding: 2px 3px ; font-weight: bold;  border-radius: 3px; text-shadow: 0px 0px 3px black; width: 35px; border: 1px solid #4C4338">
                ${runenergy}
              </div>
              <img src="https://oldschool.runescape.wiki/images/Prayer_orb.png?ebe33" style="width: 26px; height: 26px; margin-left: -5px" />
            </div>
          `;
        ]]]
  - type: custom:button-card
    entity: sensor.runelite_%username%_run_energy
    show_state: false
    show_name: false
    show_icon: false
    styles:
      custom_fields:
        info:
          - display: flex
          - flex-direction: row
          - align-items: center
          - justify-content: space-between
          - width: 100%
          - height: 100%
      card:
        - background-color: "#1e1e1e"
        - border-radius: 10px
        - height: 40px
        - width: 80px
        - padding: 6px 6px
        - position: relative
    custom_fields:
      info: |
        [[[
          const runenergy = entity.attributes.current_run_energy ?? 'N/A';
          return `
            <div style="display: flex; align-items: center; width: 100;">
              <div style="text-align:left;background-color: #685A4B; color: white; font-size: 12px; padding: 2px 3px ; font-weight: bold;  border-radius: 3px; text-shadow: 0px 0px 3px black; width: 35px; border: 1px solid #4C4338">
                ${runenergy}
              </div>
              <img src="https://oldschool.runescape.wiki/images/Run_energy_orb.png?b0ebe" style="width: 26px; height: 26px; margin-left: -5px" />
            </div>
          `;
        ]]]
  - type: custom:button-card
    entity: sensor.runelite_%username%_special_attack
    show_state: false
    show_name: false
    show_icon: false
    styles:
      custom_fields:
        info:
          - display: flex
          - flex-direction: row
          - align-items: center
          - justify-content: space-between
          - width: 100%
          - height: 100%
      card:
        - background-color: "#1e1e1e"
        - border-radius: 10px
        - height: 40px
        - width: 80px
        - padding: 6px 6px
        - position: relative
    custom_fields:
      info: |
        [[[
          const runenergy = entity.attributes.current_special_attack ?? 'N/A';
          return `
            <div style="display: flex; align-items: center; width: 100;">
              <div style="text-align:left;background-color: #685A4B; color: white; font-size: 12px; padding: 2px 3px ; font-weight: bold;  border-radius: 3px; text-shadow: 0px 0px 3px black; width: 35px; border: 1px solid #4C4338">
                ${runenergy}
              </div>
              <img src="https://oldschool.runescape.wiki/images/Special_attack_orb.png?27d06" style="width: 26px; height: 26px; margin-left: -5px" />
            </div>
          `;
        ]]]
  - type: custom:button-card
    entity: sensor.runelite_%username%_player_status
    show_name: false
    show_icon: false
    show_state: true
    state_display: |
      [[[
        const is_online = entity.attributes.is_online ?? false;
        const world = entity.attributes.world ?? -1;
        return `${is_online ? 'w: ' + world : 'offline'}`;
      ]]]
    styles:
      card:
        - background-color: "#1e1e1e"
        - border-radius: 10px
        - height: 40px
        - width: 80px
        - padding: 6px 6px
        - position: relative
```