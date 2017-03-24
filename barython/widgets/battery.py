#!/usr/bin/env python3

import logging
import os

from .base import Widget


logger = logging.getLogger("battery_widget")

BAT_DIR = "/sys/class/power_supply"
BAT_TYPE = "Battery"
BAT_STATUS = {
    "CHARGE": "full",
    "CHARGING": "charging",
    "DISCHARGING": "discharging",
    "UNKNOWN": "unknown",
}

BATTERY_INFO_FILES = {
    "capacity": ["capacity"],
    "energy_now": ["energy_now", "charge_now"],
    "energy_full": ["energy_full", "charge_full"],
    "power_now": ["power_now", "current_now"],
    "status": ["status"],
    "type": ["type"],
}


def _read_1st_and_concat(*files):
    """
    Read the first available file and concat all lines

    :param *files: files to try. Will stop at the first available file.
    """
    for f in files:
        try:
            with open(f) as f:
                return " ".join(l.strip() for l in f.readlines())
        except FileNotFoundError:
            continue


class BatteryWidget(Widget):
    """
    Show battery level
    """
    def _result_by_battery(self, battery, infos, show_batt_name=False):
        r = ""
        if show_batt_name:
            r += "{}: ".format(battery)
        r += "{}%".format(max(0, min(infos["capacity"], 100)))
        remains = max(infos["remains"], 0)
        if remains:
            r += " - {:d}:{:02d}".format(*divmod(remains, 60))
        return r

    def organize_result(self, **batteries):
        r = (" " * self.padding).join(
            self._result_by_battery(
                battery, infos, show_batt_name=len(batteries) > 1
            ) for battery, infos in sorted(batteries.items())
        )
        return super().organize_result(r)

    def list_batteries(self):
        """
        List batteries by checking each power supply device's type

        :return: yield each battery name
        """
        for component in sorted(os.listdir(BAT_DIR)):
            t = _read_1st_and_concat(*[
                os.path.join(BAT_DIR, component, type_file)
                for type_file in BATTERY_INFO_FILES.get("type", [])
            ])
            if t == BAT_TYPE:
                yield component

    def read_battery_infos(self, battery):
        infos = {}
        # Fetch all infos about the battery
        for key, val in BATTERY_INFO_FILES.items():
            try:
                info = _read_1st_and_concat(
                    *[os.path.join(BAT_DIR, battery, f) for f in val]
                )
            except FileNotFoundError:
                logger.debug(
                    "Could not read file {} for battery {}".format(
                        key, battery
                    )
                )
                continue

            try:
                infos[key] = int(info)
            except ValueError:
                infos[key] = info

        # If capacity is not directly available, computes it from energy_now
        # and energy_full
        if not infos.get("capacity", None):
            try:
                infos["capacity"] = int(
                    infos.get("energy_now", 0)/infos.get("energy_full", 0)
                )
            except ZeroDivisionError:
                infos["capacity"] = 0
        try:
            if infos["status"].lower() == BAT_STATUS["CHARGING"]:
                energy_to_charge = (
                    infos.get("energy_full", 0) - infos.get("energy_now", 0)
                )
                infos["remains"] = int(
                    60 * energy_to_charge/infos.get("power_now", 0)
                )
            elif infos["status"].lower() == BAT_STATUS["CHARGE"]:
                infos["remains"] = 0
            else:
                infos["remains"] = int(
                    60 * infos.get("energy_now", 0)/infos.get("power_now", 0)
                )
        except ZeroDivisionError:
            infos["remains"] = 0

        return infos

    def update(self, *args, **kwargs):
        batteries = {}
        for b in self.list_batteries():
            batteries[b] = self.read_battery_infos(b)
        logger.debug("Batteries: {}".format(batteries.values()))
        self.trigger_global_update(self.organize_result(**batteries))

    def __init__(self, refresh=10, *args, **kwargs):
        super().__init__(refresh=refresh, infinite=True, *args, **kwargs)
