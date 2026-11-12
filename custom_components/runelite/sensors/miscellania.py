"""Kingdom of Miscellania coffer and approval sensors.

RuneLite can only read the kingdom while you are there, so it sends the last
values it saw. Until it sends something newer, these sensors apply the daily
upkeep themselves at midnight UTC so the state stays current.
"""
from datetime import datetime, time, timedelta, timezone
import logging
import math

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_utc_time_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from ..helpers import sanitize
from custom_components.runelite.const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MAX_WITHDRAWAL_BASE = 50_000
MAX_WITHDRAWAL_ROYAL_TROUBLE = 75_000
APPROVAL_DECAY_BASE = 2.5
APPROVAL_DECAY_ROYAL_TROUBLE = 1.0
MIN_APPROVAL_PERCENT = 25
# 10% of anything below this rounds down to nothing, so the coffer stops draining there.
EMPTY_COFFER = 10
# The kingdom stops spending coins when you haven't visited for this long.
SPENDING_PAUSE = timedelta(days=30)
# A full coffer runs dry in about 200 days.
MAX_PROJECTION_DAYS = 1000


def _max_withdrawal(royal_trouble) -> int:
    return MAX_WITHDRAWAL_ROYAL_TROUBLE if royal_trouble else MAX_WITHDRAWAL_BASE


def _approval_decay(royal_trouble) -> float:
    return APPROVAL_DECAY_ROYAL_TROUBLE if royal_trouble else APPROVAL_DECAY_BASE


def _next_midnight(instant: datetime) -> datetime:
    day = instant.astimezone(timezone.utc).date() + timedelta(days=1)
    return datetime.combine(day, time.min, tzinfo=timezone.utc)


def coffer_below_time(coffer: int, max_withdrawal: int, target: int, start: datetime):
    """First midnight UTC the coffer is below target, start if it already is, None if never.

    Same projection as the RuneLite plugin, for values set from Home Assistant.
    """
    if coffer < target:
        return start
    day = _next_midnight(start)
    for _ in range(MAX_PROJECTION_DAYS):
        withdrawal = min(coffer // 10, max_withdrawal)
        if withdrawal == 0:
            return None
        coffer -= withdrawal
        if coffer < target:
            return day
        day += timedelta(days=1)
    return None


def approval_below_time(approval: float, decay_per_day: float, threshold: int, start: datetime):
    """First midnight UTC approval is below threshold, start if it already is, None if never."""
    if approval < threshold:
        return start
    if threshold <= MIN_APPROVAL_PERCENT:
        return None
    days = math.floor((approval - threshold) / decay_per_day) + 1
    return _next_midnight(start) + timedelta(days=days - 1)


def _parse_time(value):
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value))
        except ValueError:
            return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _midnights_between(start: datetime, end: datetime) -> int:
    """Number of midnights UTC after start, up to and including end."""
    if end <= start:
        return 0
    return (end.astimezone(timezone.utc).date() - start.astimezone(timezone.utc).date()).days


class MiscellaniaSensor(SensorEntity, RestoreEntity):
    """Shared plumbing: device, restore and the midnight refresh."""

    # Attributes that hold a time, so they can be parsed back on restore and update.
    _time_fields: tuple = ()
    _fields: tuple = ()

    def __init__(self, username: str, key: str, name: str, icon: str) -> None:
        super().__init__()
        self._username = username
        self._attr_unique_id = sanitize(f"runelite_{username}_{key}")
        self._attr_name = name
        self._attr_has_entity_name = True
        self._attr_icon = icon
        self._attr_state_class = "measurement"
        self._data = {field: None for field in self._fields}

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def extra_state_attributes(self):
        return dict(self._data)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, sanitize(self._username))},
            name=f"RuneLite ({self._username})",
            manufacturer="RuneLite",
            model="Old School RuneScape",
            entry_type=None,
        )

    def _set(self, field, value):
        if field in self._time_fields:
            value = _parse_time(value)
        self._data[field] = value

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            for field in self._fields:
                self._set(field, last_state.attributes.get(field))

        # The game takes its upkeep at midnight UTC; a second later so the day has rolled over.
        self.async_on_remove(
            async_track_utc_time_change(self.hass, self._handle_midnight, hour=0, minute=0, second=1)
        )

    @callback
    def _handle_midnight(self, now) -> None:
        self.async_write_ha_state()

    async def async_update(self) -> None:
        pass

    async def update_data(self, data: dict) -> None:
        for field in self._fields:
            if field in data:
                self._set(field, data[field])
        self.async_schedule_update_ha_state()

    def set_royal_trouble(self, royal_trouble: bool) -> None:
        self._data["royal_trouble"] = royal_trouble
        self._recalculate()
        self.async_schedule_update_ha_state()

    def _recalculate(self) -> None:
        """Work out the projected times, for values set from Home Assistant."""


class MiscellaniaCofferSensor(MiscellaniaSensor):
    """Coins in the Miscellania coffer, estimated from the last value RuneLite saw."""

    _time_fields = ("last_updated", "last_visit", "threshold_time", "empty_time", "spending_paused_time")
    _fields = ("coffer", "royal_trouble", "threshold") + _time_fields

    def __init__(self, username: str) -> None:
        super().__init__(username, "miscellania_coffer", "Miscellania Coffer", "mdi:treasure-chest")
        self._attr_unit_of_measurement = "coins"

    @property
    def state(self):
        coffer = self._data["coffer"]
        last_updated = self._data["last_updated"]
        if coffer is None or last_updated is None:
            return coffer

        # Spending stops once you haven't visited for 30 days.
        end = dt_util.utcnow()
        paused = self._data["spending_paused_time"]
        if paused is not None and paused < end:
            end = paused

        max_withdrawal = _max_withdrawal(self._data["royal_trouble"])
        for _ in range(_midnights_between(last_updated, end)):
            withdrawal = min(coffer // 10, max_withdrawal)
            if withdrawal == 0:
                break
            coffer -= withdrawal
        return coffer

    def mark_visited(self) -> None:
        now = dt_util.utcnow()
        if self._data["coffer"] is not None and self._data["last_updated"] is not None:
            # Start again from today's estimate, so a pause that has run out isn't drained afterwards.
            self._data["coffer"] = self.state
            self._data["last_updated"] = now
        self._data["last_visit"] = now
        self._data["spending_paused_time"] = now + SPENDING_PAUSE
        self._recalculate()
        self.async_schedule_update_ha_state()

    def set_coffer(self, coffer: int, threshold=None) -> None:
        self._data["coffer"] = coffer
        self._data["last_updated"] = dt_util.utcnow()
        if threshold is not None:
            self._data["threshold"] = threshold
        self._recalculate()
        self.async_schedule_update_ha_state()

    def _recalculate(self) -> None:
        max_withdrawal = _max_withdrawal(self._data["royal_trouble"])
        # 0 or unset picks the optimal amount: ten days of the maximum upkeep.
        if not self._data["threshold"]:
            self._data["threshold"] = max_withdrawal * 10

        coffer = self._data["coffer"]
        last_updated = self._data["last_updated"]
        if coffer is None or last_updated is None:
            return
        self._data["threshold_time"] = coffer_below_time(
            coffer, max_withdrawal, self._data["threshold"], last_updated)
        self._data["empty_time"] = coffer_below_time(coffer, max_withdrawal, EMPTY_COFFER, last_updated)


class MiscellaniaApprovalSensor(MiscellaniaSensor):
    """Miscellania approval rating, estimated from the last value RuneLite saw."""

    _time_fields = ("last_updated", "threshold_time")
    _fields = ("approval", "royal_trouble", "threshold") + _time_fields

    def __init__(self, username: str) -> None:
        super().__init__(username, "miscellania_approval", "Miscellania Approval", "mdi:crown")
        self._attr_unit_of_measurement = "%"

    @property
    def state(self):
        approval = self._data["approval"]
        last_updated = self._data["last_updated"]
        if approval is None or last_updated is None:
            return approval

        decay = _approval_decay(self._data["royal_trouble"])
        days = _midnights_between(last_updated, dt_util.utcnow())
        if days == 0:
            return approval
        return int(max(MIN_APPROVAL_PERCENT, approval - days * decay))

    def set_approval(self, approval: int, threshold=None) -> None:
        self._data["approval"] = approval
        self._data["last_updated"] = dt_util.utcnow()
        if threshold is not None:
            self._data["threshold"] = threshold
        self._recalculate()
        self.async_schedule_update_ha_state()

    def _recalculate(self) -> None:
        approval = self._data["approval"]
        last_updated = self._data["last_updated"]
        threshold = self._data["threshold"]
        if approval is None or last_updated is None or threshold is None:
            return
        self._data["threshold_time"] = approval_below_time(
            approval, _approval_decay(self._data["royal_trouble"]), threshold, last_updated)
