# Runelite OSRS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Open Source Love png1](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)

<br><br>
Custom HACS integration for tracking farming patches, farming contracts and birdhouse timers. 

## Installation

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

### Installation via HACS 

1. Ensure HACS is installed in your Home Assistant setup. If not, follow
   the [HACS installation guide](https://hacs.xyz/docs/setup/download).
2. Open the HACS panel in Home Assistant.
3. Click on custom repositories.
4. Copy the github link in the repository field: https://github.com/db1996/homeassistant_runelite.
5. Set the type field to: Integration
6. Press the add button
7. Restart Home Assistant after the installation completes.

<!-- TODO
### Installation via HACS 

1. Ensure HACS is installed in your Home Assistant setup. If not, follow
   the [HACS installation guide](https://hacs.xyz/docs/setup/download).
2. Open the HACS panel in Home Assistant.
3. Click on the `Frontend` or `Integrations` tab.
4. Click the `+` button and search for `runelite`.
5. Click `Install` to add the component to your Home Assistant setup.
6. Restart Home Assistant after the installation completes. -->

---

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
