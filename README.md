# Runelite OSRS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

<br><br>
Custom HACS integration for tracking all things OSRS

Table of contents
- [Runelite OSRS](#runelite-osrs)
  - [Installation](#installation)
    - [Via HACS](#via-hacs)
    - [Manual Installation](#manual-installation)
  - [Configuration](#configuration)
    - [Add Integration](#add-integration)
    - [Accompanying runelite plugin](#accompanying-runelite-plugin)
  - [Entities](#entities)
    - [Farming / Birdhouses](#farming--birdhouses)
    - [Skills](#skills)
    - [Activities](#activities)
    - [Dailies](#dailies)
    - [Player status](#player-status)
    - [Player status effects](#player-status-effects)
    - [Aggression timer](#aggression-timer)
  - [Events (triggers)](#events-triggers)
    - [Collection Log Notify](#collection-log-notify)
    - [Achievement diary Notify](#achievement-diary-notify)
    - [Combat Task notify](#combat-task-notify)
  - [Services (actions)](#services-actions)
    - [set\_farming\_tick\_offset](#set_farming_tick_offset)
    - [reset\_birdhouses](#reset_birdhouses)
    - [reset\_big\_compost](#reset_big_compost)
    - [reset\_all\_dailies](#reset_all_dailies)
    - [calculate\_patch\_or\_crop](#calculate_patch_or_crop)
    - [calculate\_farming\_contract](#calculate_farming_contract)
    - [Shortcut services](#shortcut-services)
    - [Patches](#patches)
    - [Farming contracts](#farming-contracts)
    - [Daily tasks](#daily-tasks)
    - [Trigger collection log notify](#trigger-collection-log-notify)
    - [Trigger achievement diary notify](#trigger-achievement-diary-notify)
    - [Trigger combat task notify](#trigger-combat-task-notify)
  - [Current updates in progress for the runelite plugin: live](#current-updates-in-progress-for-the-runelite-plugin-live)
  - [Examples](#examples)
    - [Skills overview example](#skills-overview-example)
    - [Current player stats (health etc)](#current-player-stats-health-etc)
    - [Status effects](#status-effects)
    - [Farming patch calculator](#farming-patch-calculator)
    - [Farming overview](#farming-overview)
    - [Event triggers (collection logs)](#event-triggers-collection-logs)


## Installation

### Via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=db1996&repository=homeassistant_runelite&category=integration)

1. Ensure HACS is installed in your Home Assistant setup. If not, follow
   the [HACS installation guide](https://hacs.xyz/docs/setup/download).
2. Open the HACS panel in Home Assistant.
3. Click on the `Frontend` or `Integrations` tab.
4. Click the `+` button and search for `Runelite`.
5. Click `Install` to add the component to your Home Assistant setup.
6. Restart Home Assistant after the installation completes.

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

I have built a custom runelite plugin to automatically update these entities. It will also automatically set the correct farming tick offset.

It can be found on the plugin hub named "Homeassistant", or check the repository:
https://github.com/db1996/homeassistant

---

## Entities

### Farming / Birdhouses

These entities are used to track status, crop and completion times for all farming patches, farming contract and birdhouses.

|**Entity ID**|
|----|
|sensor.runelite_%username_farming_contract
|sensor.runelite_%username_birdhouses
|sensor.runelite_%username_farming_tick_offset
|sensor.runelite_%username_seaweed_patch
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

### Skills 

Every skill has it's own sensor to track XP/level over time. There is also one for total XP. Can be used for cool graphs. 

The ID of the entity will be `sensor.runelite_%username_skill_%skilname`

The state of the sensor is the XP.
It has the following _attributes: 
`ID` Is the OSRS skill ID <br>
`Name` Friendly name of the skill<br>

`Rank` Rank on the highscores<br>
`Level` Currrent level<br>
`virtual_level` Currrent skill boost, gets updated automatically from the runelite plugin for skill boosts<br>
`Xp` Current XP

The skills automatically update every 6 hours from polling the OSRS highscores. There is a service to refetch.

Check out the [example automation here](docs/skills-overview-example.md)

### Activities

All activities found on the OSRS highscores have their own sensors, 

The ID of the entity will be `sensor.runelite_%username_activity_%skilname`

The state of the sensor is the score (KC).
It has the following _attributes: 
`ID` Is the OSRS skill ID <br>
`Name` Friendly name of the skill<br>

`Rank` Rank on the highscores<br>
`Score` Current score (KC)

### Dailies

Each daily activity has it's own sensor, the state can be -1 (missing requirements for the daily), 0 (incomplete) or 1 (complete)
The runelite plugin updates these automatically once on login. The daily staves and sand from bert are detected during playing.

The ID of the entity will be `sensor.runelite_%username_daily_%daily`

Supported daily activities right now:

- Herb boxes
- Battle staves
- Essence
- Sand
- Flax
- Arrows
- Dynamite

### Player status

Player health, prayer, special attack and run energy. These can be turned on individually in the runelite plugin to automatically update

The ID of the entities are: 
- `sensor.runelite_%username_health`: Technically duplicate of the virtual_level of the hitpoints skill
- `sensor.runelite_%username_prayer`: Technically duplicate of the virtual_level of the prayer skill
- `sensor.runelite_%username_run_energy`: Current run energy. IF you turn this one on it will result in a lot of calls unless you turn on the new throttle setting
- `sensor.runelite_%username_special_attack`: Current special attack

The state will be the number, and it has an attribute: `current_health`, `current_prayer`, `current_special_attack` or `current_run_energy` 

Check out the [example automation here](docs/player-status-example.md)

### Player status effects

For now, contains `poison` or `venom`, I will add more in the future on the runelite plugin side of things

The ID of the entity will be `sensor.runelite_%username_status_effects`
It contains an attribute `current_status_effects`, which contains a list of the following attributes

- `name`    Name of the effect, for now limited to `Poison` or `Venom`
- `number`  Right now represents the damage number. But in the future for skill boosts for example, it will be the boost so could be below 0 as well.
- `time`    Is not yet used, in the future I want to add a calculation to estimate the time for some of them

Check out the [example automation here](docs/status-effects-example.md)

### Aggression timer

Player aggression timer, logic is the same as the internal runelite aggression timer plugin.

The ID of the entity will be `sensor.runelite_%username_aggression`

And it has these attributes:

- `status`: current status, also it's state, one of these values: `unknown`, `active`, `safe`
- `seconds`: current amount of seconds left
- `ticks`: current amount of ticks left

## Events (triggers)

When playing with the runelite plugin active, it can send events you can use as triggers in automations. 

### Collection Log Notify

`runelite_collection_log_notify`

Has to be turned on in the runelite plugin settings. Will trigger when a collection log slot is unlocked.

Contains the following data attributes:

- `item_name`: Name of the unlocked item

Check out the [example automation here](docs/event_triggers-example.md)

You can trigger this yourself by calling the service [calling the service](#trigger-collection-log-notify)


### Achievement diary Notify

`runelite_achievement_diary_notify`

Has to be turned on in the runelite plugin settings. Will trigger when an achievement diary task is completed

Contains the following data attributes:

- `task_name`: Name of the region
- `tier`: Tier of the diary

Check out the [example automation here](docs/event_triggers-example.md)

You can trigger this yourself by calling the service [calling the service](#trigger-achievement-diary-notify)

### Combat Task notify

`runelite_combat_task_notify`

Has to be turned on in the runelite plugin settings. Will trigger when an achievement diary task is completed

Contains the following data attributes:

- `task_name`: Name of the task
- `tier`: Tier of the diary

Check out the [example automation here](docs/event_triggers-example.md)

You can trigger this yourself by calling the service [calling the service](#trigger-combat-task-notify)

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

### reset_big_compost

Sets the completion time of the big compost bin. This just sets it to the current time + 90 minutes. 

|**Inputs**|Info|
|----|----|
|Username|Only needed if you have more than 1 username hub added to the integration.

### reset_all_dailies

Sets all daily activities to 0.

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

### Daily tasks

Each daily task has it's own reset/done service. Reset to set it back to 0 (incomplete), done to set it to 1 (complete)
The services will be called: `daily_done_%activity%`

### Trigger collection log notify

You can call this service to test the collection log event. This is also the exact service runelite calls when it is detected.

The services is called: `runelite.trigger_collection_log_notify`


### Trigger achievement diary notify

You can call this service to test the achievemtnt diary event. This is also the exact service runelite calls when it is detected.

The services is called: `runelite.trigger_achievement_diary_notify`

|**Inputs**|Info|
|----|----|
|task_name|Region of the diary
|tier|Tier of the task

### Trigger combat task notify

You can call this service to test the combat task event. This is also the exact service runelite calls when it is detected.

The services is called: `runelite.trigger_combat_task_notify`

|**Inputs**|Info|
|----|----|
|task_name|Name of the completed task|
|tier|Tier of the task

## Current updates in progress for the runelite plugin: live

The latest updates are all live in runelite right now!

## Examples

I have various examples for dashboards and automations that I use.

### [Skills overview example](docs/skills-overview-example.md)
### [Current player stats (health etc)](docs/player-status-example.md)
### [Status effects](docs/status-effects-example.md)
### [Farming patch calculator](docs/calculator-patches-example.md)
### [Farming overview](docs/farming-overview-example.md)
### [Event triggers (collection logs)](docs/event_triggers-example.md)



