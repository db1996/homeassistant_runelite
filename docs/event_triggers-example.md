# Trigger for runelite event example

Below is the example for the collection log notify. Any event listed [here](../README.md#events-triggers) can be used instead of `runelite_collection_log_notify`, 

any of the data attributes can be accesed like `trigger.event.data.item_name`

Create a new automation -> edit yaml (top right corner)

``` yaml
alias: Collection Log Notify
description: ""
triggers:
  - event_type: runelite_collection_log_notify
    trigger: event
actions:
  - action: notify.mobile_phone
    metadata: {}
    data:
      message: "{{ trigger.event.data.item_name }}"
      title: Collection log unlocked
```