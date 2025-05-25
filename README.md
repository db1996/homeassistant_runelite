# Runelite OSRS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Open Source Love png1](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)

<br><br>
Custom HACS integration for tracking farming patches, farming contracts and birdhouse timers. 

## Installation

### Via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=db1996&repository=homeassistant_runelite&category=integration)

1. In Home Assistant, open **HACS** in the sidebar.
2. Click the **⋮** menu (top right) and select **Custom repositories**.
3. Add this repository:
   - **URL**: `https://github.com/db1996/homeassistant_runelite`
   - **Category**: **Integration**
4. Back in **HACS → Integrations**, locate **runelite** and click **Install**.
5. After installation, go to **Settings → System → Integrations**, click **+ Add integration**, then search for **runelite**.

### Manual Installation

1. Navigate to your Home Assistant configuration directory (where your `configuration.yaml` is located).
2. Create a folder named `custom_components` if it doesn't exist.
3. Inside the `custom_components` folder, create another folder named `runelite`.
4. Clone this repository or download the source code and copy all files from the `custom_components/runelite/`
   directory to the newly created `runelite` folder.
5. Restart Home Assistant to load the custom component.

After following these steps, your directory structure should look like this:

```markdown
custom_components/
runelite/
__init__.py
config_flow.py
manifest.json
sensor.py
services.py
...
```

<!-- TODO
### Installation via HACS 

1. Ensure HACS is installed in your Home Assistant setup. If not, follow
   the [HACS installation guide](https://hacs.xyz/docs/setup/download).
2. Open the HACS panel in Home Assistant.
3. Click on the `Frontend` or `Integrations` tab.
4. Click the `+` button and search for `runelite`.
5. Click `Install` to add the component to your Home Assistant setup.
6. Restart Home Assistant after the installation completes. -->

## Configuration

### Add Integration

1. Go to the **Settings** → **Devices & Services** page in Home Assistant.
2. Click **Add Integration** and search for `runelite`.
3. Follow the on-screen instructions to complete the setup.
    - Provide your OSRS username
    - You can provide your farming tick offset, this can be found in the timers plugin in runelite.
        Set this to 0 if you can't find it.
    - You can create entities for multiple usernames.

After completing the config flow, the integration will automatically create sensors under a hub for all the timers. And one for the farming tick offset, you can change the sensor's value to change it. 


### Accompanying runelite plugin

I have built a custom runelite plugin to automatically update these entities. It will also automatically set the correct farming tick offset. I am going through the process of getting it in the plugin hub right now.

Repository: https://github.com/db1996/homeassistant

---

## Entities

These entites are created with the following attributes

|**Entity ID**|
|----|
|sensor.runelite_%username_farming_contract
|sensor.runelite_%username_birdhouses
|sensor.runelite_%username_farming_tick_offset
|sensor.runelite_%username_herb_patch
|sensor.runelite_%username_tree_patch
|sensor.runelite_%username_fruit_tree_patch
|sensor.runelite_%username_flower_patch
|sensor.runelite_%username_allotment_patch
|sensor.runelite_%username_bush_patch
|sensor.runelite_%username_mushroom_patch
|sensor.runelite_%username_cactus_patch
|sensor.runelite_%username_potato_cactus_patch
|sensor.runelite_%username_spirit_tree_patch
|sensor.runelite_%username_hardwood_patch
|sensor.runelite_%username_redwood_patch
|sensor.runelite_%username_hespori_patch

Except for the farming tick offset, which is just a number from -30 to 30, all of the sensors have these attributes:

`status` ready, in_progress, other, not_planted <br>
`completion_time` Next completion time, timezone aware<br>

`crop_type` not always set, the only patch type with varying growth times are: tree, hardwood tree, allotment, bush. So only the available seeds are an input for those. that includes the farming contract.<br>
`patch_type` This is set for all the patch entities. For the farming contract it is always needed. For the other patches it is an attribute only for ease of use in creating a dashboard.

---

## Services (actions)

There are quite a few services to set new timers in different ways. 

### set_farming_tick_offset

Sets the farming growth tick offset of your account. This differs per runescape account and this dictates exactly when the crop will be done. Otherwise the calculation can be very off. 

|**Inputs**|Info|
|----|----|
|Username|Only needed if you have more than 1 username hub added to the integration.
|Tick Offset|The tick offset to set for the farming patch. This is a number between -30 and 30

### reset_birdhouses

Sets the completion time of a birdhouse run to the entity. This just sets it to the current time + 50 minutes. 

|**Inputs**|Info|
|----|----|
|Username|Only needed if you have more than 1 username hub added to the integration.


### calculate_patch_or_crop

This is the action most others are based on. Just with shortcuts which i will explain down below.
It sets the entity of the corresponding patch to in_progress and sets the completion time.

|**Inputs**|Info|
|----|----|
|Username|Only needed if you have more than 1 username hub added to the integration.
|Patch Type|Each patch type has it's own growth tick cycle.<br> The reason cactus and potato cactus are seperate is because they have very different cycles. A technical limitation<br>`herb`,`hespori`,`tree`,`fruit_tree`<br>`cactus`,`hardwood`,`spirit_tree`,`allotment`,`bush`,`flower`,`mushroom`,`potato_cactus`
|Crop Type|If this is set to a crop of a different patch type than the patch type input, it will override the patch type.<br>`oak`,`willow`,`maple`,`yew`,`magic`,<br>`strawberry`,`watermelon`,`snape_grass`,`teak`,`mahogany`<br>`whiteberry`,`poison_ivy`,`jangerberry`,`redberry`,`cadavaberry`,`dwellberry`<br>`potato`,`onion`,`cabbage`,`tomato`,`sweetcorn`

### calculate_farming_contract

This does the exact same as the above. But instead of setting the patch type entity, it sets the farming contract entity

|**Inputs**|Info|
|----|----|
|Username|Only needed if you have more than 1 username hub added to the integration.
|Patch Type|Each patch type has it's own growth tick cycle.<br> The reason cactus and potato cactus are seperate is because they have very different cycles. A technical limitation<br>`herb`,`hespori`,`tree`,`fruit_tree`,<br>`cactus`,`hardwood`,`spirit_tree`,`allotment`,`bush`,`flower`,`mushroom`,`potato_cactus`
|Crop Type|If this is set to a crop of a different patch type than the patch type input, it will override the patch type.<br>`oak`,`willow`,`maple`,`yew`,`magic`<br>`strawberry`,`watermelon`,`snape_grass`,`teak`,`mahogany`<br>`whiteberry`,`poison_ivy`,`jangerberry`,`redberry`,`cadavaberry`,`dwellberry`<br>`potato`,`onion`,`cabbage`,`tomato`,`sweetcorn`


### Shortcut services

I created shortcut services, mainly because it made it easier to create a dashboard where you can set the various patches easily. 

### Patches 

Every single patch type has it's own service. For example `herb_patch` will calculate the next herb patch completion and sets it's entity. For patch types without a crop type, the only input is an optional username for when you use multiple usernames. The patch types with a crop type the input is available with the correct crops. 

### Farming contracts

Each farming contract crop type has it's own service. For example `farming_contract_herb`. The arguments are the same as the ones for patches.


## Dashboard overview example

I have a very simple dashboard component, made with https://github.com/custom-cards/secondaryinfo-entity-row
This shows a list of some of the patches and farming contract, their status, and completion time.
Replace %username with your own username (lowercase, the same as the entity ids)


```yaml
type: entities
entities:
  - entity: sensor.runelite_%username_hespori_patch
    type: custom:secondaryinfo-entity-row
    name: Hespori status
    secondary_info: >
      {% set sen = 'sensor.runelite_%username_hespori_patch' %}  {% if
      is_state(sen, 'in_progress') %}
        {% set ts_obj = state_attr(sen, 'completion_time') %}
        {% if ts_obj %}
           {{ "ETA: " + ts_obj.astimezone().strftime('%H:%M %d-%m') }}
        {% endif %}
      {% endif %}
  - entity: sensor.runelite_%username_farming_contract
    type: custom:secondaryinfo-entity-row
    name: Farming contract status
    secondary_info: >
      {% set sen = 'sensor.runelite_%username_farming_contract' %}  {% if
      is_state(sen, 'in_progress') %}
        {% set ts_obj = state_attr(sen, 'completion_time') %}
        {% if ts_obj %}
           {{ "ETA: " + ts_obj.astimezone().strftime('%H:%M %d-%m') }}
        {% endif %}
      {% endif %}
  - entity: sensor.runelite_%username_herb_patch
    type: custom:secondaryinfo-entity-row
    name: Herb status
    secondary_info: >
      {% set sen = 'sensor.runelite_%username_herb_patch' %}  {% if
      is_state(sen, 'in_progress') %}
        {% set ts_obj = state_attr(sen, 'completion_time') %}
        {% if ts_obj %}
           {{ "ETA: " + ts_obj.astimezone().strftime('%H:%M %d-%m') }}
        {% endif %}
      {% endif %}
  - entity: sensor.runelite_%username_birdhouses
    type: custom:secondaryinfo-entity-row
    name: Birdhouses status
    secondary_info: >
      {% set sen = 'sensor.runelite_%username_birdhouses' %}  {% if
      is_state(sen, 'in_progress') %}
        {% set ts_obj = state_attr(sen, 'completion_time') %}
        {% if ts_obj %}
           {{ "ETA: " + ts_obj.astimezone().strftime('%H:%M %d-%m') }}
        {% endif %}
      {% endif %}
  - entity: sensor.runelite_%username_tree_patch
    type: custom:secondaryinfo-entity-row
    name: Tree patch status
    secondary_info: >
      {% set sen = 'sensor.runelite_%username_tree_patch' %}  {% if
      is_state(sen, 'in_progress') %}
        {% set ts_obj = state_attr(sen, 'completion_time') %}
        {% if ts_obj %}
           {{ "ETA: " + ts_obj.astimezone().strftime('%H:%M %d-%m') }}
        {% endif %}
      {% endif %}
  - entity: sensor.runelite_%username_hardwood_patch
    type: custom:secondaryinfo-entity-row
    name: Hardwood patch status
    secondary_info: >
      {% set sen = 'sensor.runelite_%username_hardwood_patch' %}  {% if
      is_state(sen, 'in_progress') %}
        {% set ts_obj = state_attr(sen, 'completion_time') %}
        {% if ts_obj %}
           {{ "ETA: " + ts_obj.astimezone().strftime('%H:%M %d-%m') }}
        {% endif %}
      {% endif %}
```


## Dashboard calculate patches and farming contract buttons

A bunch of buttons and dropdowns to set various farming patches. This uses mushroom cards:
https://github.com/piitaya/lovelace-mushroom

And for the calls: 
https://github.com/Nerwyn/custom-card-features

For patch types:

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: Calculate patches
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.runelite_%username_herb_patch
        name: Herb
        icon: mdi:sprout
        tap_action:
          action: call-service
          service: runelite.herb_patch
          data: {}
        secondary_info: none
        primary_info: name
      - type: custom:mushroom-entity-card
        entity: sensor.runelite_%username_hespori_patch
        name: Hespori
        icon: mdi:tree-outline
        tap_action:
          action: call-service
          service: runelite.hespori_patch
          data: {}
        secondary_info: none
        primary_info: name
      - type: custom:mushroom-entity-card
        entity: sensor.runelite_%username_redwood_patch
        name: Redwood
        icon: mdi:tree
        tap_action:
          action: call-service
          service: runelite.redwood_patch
          data: {}
        secondary_info: none
        primary_info: name
  - type: horizontal-stack
    cards:
      - features:
          - type: custom:service-call
            entries:
              - type: dropdown
                entity_id: sensor.runelite_%username_tree_patch
                options:
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Oak
                    tap_action:
                      action: perform-action
                      perform_action: runelite.tree_patch
                      data:
                        crop_type: oak
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Willow
                    tap_action:
                      action: perform-action
                      perform_action: runelite.tree_patch
                      data:
                        crop_type: willow
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Maple
                    tap_action:
                      action: perform-action
                      perform_action: runelite.tree_patch
                      data:
                        crop_type: maple
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Yew
                    tap_action:
                      action: perform-action
                      perform_action: runelite.tree_patch
                      data:
                        crop_type: yew
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Magic
                    tap_action:
                      action: perform-action
                      perform_action: runelite.tree_patch
                      data:
                        crop_type: magic
        type: tile
        name: Tree
        icon: mdi:pine-tree
        entity: sensor.runelite_%username_tree_patch
        hide_state: true
      - features:
          - type: custom:service-call
            entries:
              - type: dropdown
                entity_id: sensor.runelite_%username_hardwood_patch
                options:
                  - entity_id: sensor.runelite_%username_hardwood_patch
                    label: Teak
                    tap_action:
                      action: perform-action
                      perform_action: runelite.hardwood_patch
                      data:
                        crop_type: teak
                  - entity_id: sensor.runelite_%username_hardwood_patch
                    label: Mahogany
                    tap_action:
                      action: perform-action
                      perform_action: runelite.hardwood_patch
                      data:
                        crop_type: mahogany
        type: tile
        name: Hardwood
        icon: mdi:pine-tree
        entity: sensor.runelite_%username_hardwood_patch
        hide_state: true
```


For farming contracts:

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: Farming contract
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.runelite_%username_herb_patch
        name: Herb
        icon: mdi:sprout
        tap_action:
          action: call-service
          service: runelite.farming_contract_herb
          data: {}
        secondary_info: none
        primary_info: name
      - type: custom:mushroom-entity-card
        entity: sensor.runelite_%username_redwood_patch
        name: Redwood
        icon: mdi:tree
        tap_action:
          action: call-service
          service: runelite.farming_contract_redwood
          data: {}
        secondary_info: none
        primary_info: name
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.runelite_%username_flower_patch
        name: Flower
        icon: mdi:flower
        tap_action:
          action: call-service
          service: runelite.farming_contract_flower
          data: {}
        secondary_info: none
        primary_info: name
      - type: custom:mushroom-entity-card
        entity: sensor.runelite_%username_fruit_tree_patch
        name: Fruit tree
        icon: mdi:food-apple
        tap_action:
          action: call-service
          service: runelite.farming_contract_fruit_tree
          data: {}
        secondary_info: none
        primary_info: name
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.runelite_%username_cactus_patch
        name: Cactus
        icon: mdi:cactus
        tap_action:
          action: call-service
          service: runelite.farming_contract_cactus
          data: {}
        secondary_info: none
        primary_info: name
      - type: custom:mushroom-entity-card
        entity: sensor.runelite_%username_potato_cactus_patch
        name: Potato Cactus
        icon: mdi:cactus
        tap_action:
          action: call-service
          service: runelite.farming_contract_potato_cactus
          data: {}
        secondary_info: none
        primary_info: name
  - type: horizontal-stack
    cards:
      - features:
          - type: custom:service-call
            entries:
              - type: dropdown
                entity_id: sensor.runelite_%username_tree_patch
                options:
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Oak
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_tree
                      data:
                        crop_type: oak
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Willow
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_tree
                      data:
                        crop_type: willow
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Maple
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_tree
                      data:
                        crop_type: maple
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Yew
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_tree
                      data:
                        crop_type: yew
                  - entity_id: sensor.runelite_%username_tree_patch
                    label: Magic
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_tree
                      data:
                        crop_type: magic
        type: tile
        name: Tree
        icon: mdi:pine-tree
        entity: sensor.runelite_%username_tree_patch
        hide_state: true
      - features:
          - type: custom:service-call
            entries:
              - type: dropdown
                entity_id: sensor.runelite_%username_allotment_patch
                options:
                  - entity_id: sensor.runelite_%username_allotment_patch
                    label: Potato
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_allotment
                      data:
                        crop_type: potato
                  - entity_id: sensor.runelite_%username_allotment_patch
                    label: Onion
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_allotment
                      data:
                        crop_type: onion
                  - entity_id: sensor.runelite_%username_allotment_patch
                    label: Cabbage
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_allotment
                      data:
                        crop_type: cabbage
                  - entity_id: sensor.runelite_%username_allotment_patch
                    label: Tomato
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_allotment
                      data:
                        crop_type: tomato
                  - entity_id: sensor.runelite_%username_allotment_patch
                    label: Sweetcorn
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_allotment
                      data:
                        crop_type: sweetcorn
                  - entity_id: sensor.runelite_%username_allotment_patch
                    label: Strawberry
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_allotment
                      data:
                        crop_type: strawberry
                  - entity_id: sensor.runelite_%username_allotment_patch
                    label: Watermelon
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_allotment
                      data:
                        crop_type: watermelon
                  - entity_id: sensor.runelite_%username_allotment_patch
                    label: Snape Grass
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_allotment
                      data:
                        crop_type: snape_grass
        type: tile
        name: Allotment
        icon: mdi:grass
        entity: sensor.runelite_%username_allotment_patch
        hide_state: true
      - features:
          - type: custom:service-call
            entries:
              - type: dropdown
                entity_id: sensor.runelite_%username_bush_patch
                options:
                  - entity_id: sensor.runelite_%username_bush_patch
                    label: Whiteberry
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_bush
                      data:
                        crop_type: whiteberry
                  - entity_id: sensor.runelite_%username_bush_patch
                    label: Poison Ivy
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_bush
                      data:
                        crop_type: poison_ivy
                  - entity_id: sensor.runelite_%username_bush_patch
                    label: Jangerberry
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_bush
                      data:
                        crop_type: jangerberry
                  - entity_id: sensor.runelite_%username_bush_patch
                    label: Redberry
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_bush
                      data:
                        crop_type: redberry
                  - entity_id: sensor.runelite_%username_bush_patch
                    label: Cadavaberry
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_bush
                      data:
                        crop_type: cadavaberry
                  - entity_id: sensor.runelite_%username_bush_patch
                    label: Dwellberry
                    tap_action:
                      action: perform-action
                      perform_action: runelite.farming_contract_bush
                      data:
                        crop_type: dwellberry
        type: tile
        name: Bush
        icon: mdi:spa
        entity: sensor.runelite_%username_bush_patch
        hide_state: true
```
