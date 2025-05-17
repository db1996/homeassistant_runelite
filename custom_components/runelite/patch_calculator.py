import logging
from datetime import datetime, timedelta, timezone
from .const import PATCH_TYPE_DATA, CROP_TYPE_DATA, DOMAIN
from homeassistant.core import HomeAssistant
_LOGGER = logging.getLogger(__name__)

class PatchCalculator:
    """
    A class to calculate the growth and harvest times of patches.
    """
    hass: HomeAssistant
    username: str

    i_patch_type: str = None
    i_crop_type: str = None
    farming_tick_offset: int = 0  # Offset in minutes for farming ticks

    # Calculated values
    start_time: datetime = None
    completion_time: datetime = None
    patch_type: str = None


    def __init__(self, hass: HomeAssistant, username: str):
        self.hass = hass
        self.start_time = datetime.now(timezone.utc)
        self.username = username

    def calculate(self, crop_type: str = None, patch_type: str = None, status: str = None) -> dict:
        
        self.i_patch_type = patch_type
        self.i_crop_type = crop_type
        self.get_farming_tick_offset()
        calculation_data = self.calculate_crop_completion_time(patch_type=self.i_patch_type, crop_type=self.i_crop_type)
        if calculation_data:
            self.patch_type = calculation_data["crop_patch_type"]
            self.completion_time = calculation_data["completion_time"]
            _LOGGER.info(
                f"Patch type: {self.patch_type}, crop: {self.i_crop_type}, Completion time (UTC): {self.completion_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return {
                "status": status,
                "patch_type": self.patch_type,
                "crop_type": self.i_crop_type,
                "completion_time": self.completion_time,
            }
        return None

    def get_farming_tick_offset(self):
        """Get the farming tick offset in minutes."""
        offset_entity_id = f"sensor.runelite_{self.username}_farming_tick_offset"
        _LOGGER.info(f"Getting farming tick offset for entity: {offset_entity_id}")
        integration_data = self.hass.data.get(DOMAIN, {})
        for entry_id, entry_data in integration_data.items():
            sensor_entity = entry_data.get("entities", {}).get(offset_entity_id)
            if(sensor_entity):
                self.farming_tick_offset = sensor_entity._farming_tick_offset
                _LOGGER.info(f"Farming tick offset: {self.farming_tick_offset}")
                return


    def calculate_crop_completion_time(self, crop_type=None, patch_type=None):
        """Calculates the next completion time of a planted crop in UTC."""
        self.start_time = datetime.now(timezone.utc)
        crop_patch_type = None
        growth_cycles = None
        _LOGGER.info(
            f"Calculating completion time for crop type '{crop_type}' or patch type '{patch_type}'."
        )
        if crop_type:
            if crop_type not in CROP_TYPE_DATA:
                _LOGGER.error(f"Crop type '{crop_type}' is not recognized.")
                return None
            crop_patch_type = CROP_TYPE_DATA[crop_type]["patch_type"]
            growth_cycles = CROP_TYPE_DATA[crop_type]["cycles"]
        elif patch_type:
            crop_patch_type = patch_type
            if patch_type in PATCH_TYPE_DATA and "global_cycles" in PATCH_TYPE_DATA[patch_type]:
                growth_cycles = PATCH_TYPE_DATA[patch_type]["global_cycles"]
            else:
                _LOGGER.error(
                    f"Patch type '{patch_type}' provided without a crop type, but it does not have 'global_cycles' defined."
                )
                return None
        else:
            _LOGGER.error("Either 'crop_type' or 'patch_type' must be provided.")
            return None

        if crop_patch_type not in PATCH_TYPE_DATA:
            _LOGGER.error(f"Patch type '{crop_patch_type}' not found in patch data.")
            return None

        patch_info = PATCH_TYPE_DATA.get(crop_patch_type, {})
        cycle_length_minutes = patch_info.get("cycle_length_minutes")
        growth_ticks = patch_info.get("growth_ticks")
        growth_ticks_days = patch_info.get("growth_ticks_days")

        if cycle_length_minutes is None:
            _LOGGER.error(f"Could not find 'cycle_length_minutes' for patch type '{crop_patch_type}'.")
            return None

        if growth_cycles is None:
            _LOGGER.error("Could not determine the number of growth cycles.")
            return None

        next_completion_time_utc = None

        if growth_ticks:
            next_completion_time_utc = None

            patch_global_cycles = PATCH_TYPE_DATA.get(crop_patch_type, {}).get("global_cycles")
            if patch_global_cycles is None and growth_cycles is None:
                _LOGGER.error(f"Could not determine the number of growth cycles for '{crop_patch_type}'.")
                return None

            total_cycles = growth_cycles if growth_cycles is not None else patch_global_cycles

            for cycle in range(total_cycles):
                for i, tick_str in enumerate(growth_ticks):
                    tick_hour_str, tick_minute_str = tick_str.split(":")
                    target_minute = int(tick_minute_str)
                    target_hour = self.start_time.hour if tick_hour_str == "*" else int(tick_hour_str)

                    # Calculate the target time for this specific cycle
                    target_time_utc = self.start_time.replace(
                        hour=target_hour, minute=target_minute, second=0, microsecond=0
                    )
                    cycle_start_offset = timedelta(minutes=cycle * cycle_length_minutes)
                    target_time_utc += cycle_start_offset

                    target_time_utc_offset = target_time_utc + timedelta(minutes=self.farming_tick_offset)

                    if target_time_utc_offset > self.start_time:
                        # This is the next growth tick
                        remaining_cycles = total_cycles - 1
                        completion_delay = timedelta(minutes=remaining_cycles * cycle_length_minutes)
                        next_completion_time_utc = target_time_utc_offset + completion_delay
                        _LOGGER.info(
                            f"Next growth tick found at {target_time_utc_offset.strftime('%H:%M:%S UTC')} for '{crop_patch_type}'. Remaining cycles: {remaining_cycles}"
                        )
                        return {"crop_patch_type": crop_patch_type, "completion_time": next_completion_time_utc}

            # Fallback if no future tick found in the loop (should be rare)
            first_tick_str = growth_ticks[0]
            tick_hour_str, tick_minute_str = first_tick_str.split(":")
            target_minute = int(tick_minute_str)
            target_hour = self.start_time.hour if tick_hour_str == "*" else int(tick_hour_str)
            next_cycle_start_utc = self.start_time + timedelta(minutes=cycle_length_minutes)
            target_first_tick_next_cycle_utc = next_cycle_start_utc.replace(
                hour=target_hour, minute=target_minute, second=0, microsecond=0
            )
            remaining_cycles_fallback = total_cycles - 1
            completion_delay_fallback = timedelta(minutes=remaining_cycles_fallback * cycle_length_minutes)
            next_completion_time_utc = (
                target_first_tick_next_cycle_utc
                + timedelta(minutes=self.farming_tick_offset)
                + completion_delay_fallback
            )
            return {"crop_patch_type": crop_patch_type, "completion_time": next_completion_time_utc}

        elif growth_ticks_days:
            _LOGGER.info(f"Calculating completion time based on daily growth ticks for '{crop_patch_type}'.")
            start_date = datetime(2025, 4, 6, tzinfo=timezone.utc)  # Sunday, April 6, 2025
            self.start_time = datetime.now(timezone.utc)
            elapsed_days = (self.start_time.date() - start_date.date()).days
            days_in_cycle = 0
            for day_str in growth_ticks_days.keys():
                try:
                    day_int = int(day_str)
                    if day_int > days_in_cycle:
                        days_in_cycle = day_int
                except ValueError:
                    _LOGGER.error(f"Invalid day key in growth_ticks_days: {day_str}")
                    return None  # Or handle the error as needed
            if days_in_cycle == 0 and growth_ticks_days:
                # If there are keys but none were valid integers, or if the dict is not empty but max remains 0
                _LOGGER.warning("Could not determine the number of days in the growth cycle.")
                return None  # Or handle as needed

            current_growth_day = (elapsed_days % days_in_cycle) + 1
            _LOGGER.info(
                f"Current elapsed days: {elapsed_days}, Days in cycle: {days_in_cycle}, Current growth day: {current_growth_day}"
            )

            target_growth_times = growth_ticks_days.get(str(current_growth_day))
            if not target_growth_times:
                _LOGGER.warning(
                    f"No growth ticks found for day {current_growth_day} of '{crop_patch_type}'. Falling back to cycle length."
                )
                next_completion_time_utc = self.start_time + timedelta(minutes=cycle_length_minutes * growth_cycles)
                return {"crop_patch_type": crop_patch_type, "completion_time": next_completion_time_utc}

            next_tick_time_utc = None

            for growth_time_str in target_growth_times:
                tick_hour_str, tick_minute_str = growth_time_str.split(":")
                target_hour = int(tick_hour_str)
                target_minute = int(tick_minute_str)

                # Create a UTC datetime object for today at the target time
                target_time_today_utc = self.start_time.replace(
                    hour=target_hour, minute=target_minute, second=0, microsecond=0
                )

                # If the target time today is in the past, consider it for the next cycle if needed
                if target_time_today_utc <= self.start_time:
                    # If all ticks for today have passed, we need to look at future days in the cycle
                    pass  # Handled later

                target_time_utc_offset = target_time_today_utc + timedelta(minutes=self.farming_tick_offset)

                if target_time_utc_offset > self.start_time:
                    next_tick_time_utc = target_time_utc_offset
                    break

            if next_tick_time_utc:
                # Calculate the completion time based on the next tick and remaining cycles
                remaining_cycles = growth_cycles - 1
                completion_delay = timedelta(minutes=remaining_cycles * cycle_length_minutes)
                next_completion_time_utc = next_tick_time_utc + completion_delay
            else:
                # If no future tick found for the current day, we need to look at the next days in the cycle
                for day_offset in range(1, days_in_cycle + 1):
                    next_growth_day = (current_growth_day + day_offset - 1) % days_in_cycle + 1
                    next_day_target_times = growth_ticks_days.get(str(next_growth_day))
                    if next_day_target_times:
                        future_date = self.start_time.date() + timedelta(days=day_offset)
                        for growth_time_str in next_day_target_times:
                            tick_hour_str, tick_minute_str = growth_time_str.split(":")
                            target_hour = int(tick_hour_str)
                            target_minute = int(tick_minute_str)

                            target_time_future_utc = datetime(
                                future_date.year,
                                future_date.month,
                                future_date.day,
                                hour=target_hour,
                                minute=target_minute,
                                second=0,
                                microsecond=0,
                                tzinfo=timezone.utc,
                            )
                            target_time_utc_offset = target_time_future_utc + timedelta(
                                minutes=self.farming_tick_offset
                            )

                            if target_time_utc_offset > self.start_time:
                                next_completion_time_utc = target_time_utc_offset + timedelta(
                                    minutes=(growth_cycles - 1) * cycle_length_minutes
                                )
                                _LOGGER.info(
                                    f"Next growth tick found on day {next_growth_day} ({future_date.strftime('%Y-%m-%d')}) at {target_time_utc_offset.strftime('%H:%M:%S UTC')}"
                                )
                                return {"crop_patch_type": crop_patch_type, "completion_time": next_completion_time_utc}
                        if next_completion_time_utc:
                            break  # Found a future tick

            if not next_completion_time_utc:
                _LOGGER.warning(
                    f"Could not find a future growth tick for '{crop_patch_type}'. Falling back to cycle length."
                )
                next_completion_time_utc = self.start_time + timedelta(minutes=cycle_length_minutes * growth_cycles)
        else:
            next_completion_time_utc = self.start_time + timedelta(minutes=cycle_length_minutes * growth_cycles)
            _LOGGER.warning(
                f"No 'growth_ticks' found for '{crop_patch_type}'. Calculating completion based on cycle length only."
            )

        return {"crop_patch_type": crop_patch_type, "completion_time": next_completion_time_utc}