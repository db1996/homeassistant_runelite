# Status effects: poison or venom

For now the only status effects shown are poison and venom. But maybe more will follow in the future, leave requests in the issues!

This example is the blue part of the image below, it works well on desktop as well as mobile

<img src="images/skill_status.jpg" alt="Prayer Tile Example" width="300px">

## HACS used in the example

- lovelace button-card: https://github.com/custom-cards/button-card

## Example

Create a markdown card with the following content:

```yaml
{% for effect in state_attr('sensor.runelite_%username%_status_effects', 'current_status_effects') %}
- **{{ effect.name | capitalize }}**: {{ effect.number }} damage
{% endfor %}

```
