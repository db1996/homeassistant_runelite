# Dashboard farming overview example

It is a very simple dashboard component, have not made it ncie looking yet yet

This shows a list of some of the patches and farming contract, their status, and completion time.
Replace %username with your own username (lowercase, the same as the entity ids)

## HACS used in the example

- custom-cards/secondaryinfo-entity-row: https://github.com/custom-cards/secondaryinfo-entity-row

## Example

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