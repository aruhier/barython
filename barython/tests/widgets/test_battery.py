
import pytest

import barython.widgets.battery
from barython.panel import Panel
from barython.screen import Screen
from barython.widgets.battery import BatteryWidget


BATTERIES = {
    "BAT0": {
        "capacity": 95, "energy_now": 40634000, "energy_full": 41965000,
        "power_now": 17611000, "status": "Discharging", "type": "Battery"
    },
    "BAT1": {
        "capacity": 40, "energy_now": 20634000, "energy_full": 51965000,
        "power_now": 15611000, "status": "Charging", "type": "Battery"
    }
}


@pytest.fixture
def one_battery_dir(tmpdir, monkeypatch):
    """
    Simulate a battery directory, with only one battery BAT0
    """
    battery = "BAT0"
    power_supply_dir = tmpdir
    battery_dir = power_supply_dir.mkdir(battery)

    infos = BATTERIES[battery]
    for key, val in infos.items():
        f = battery_dir.join(key)
        f.write(val)

    monkeypatch.setattr(barython.widgets.battery, "BAT_DIR",
                        str(power_supply_dir))
    return power_supply_dir


@pytest.fixture
def multiple_batteries_dir(tmpdir, monkeypatch):
    """
    Simulate a battery directory, with only 2 batteries and one AC
    """
    power_supply_dir = tmpdir

    for battery, infos in BATTERIES.items():
        battery_dir = power_supply_dir.mkdir(battery)

        for key, val in infos.items():
            f = battery_dir.join(key)
            f.write(val)

    # In real world, will never have that name, but test if it detects
    # correctly the batteries without being based on their names
    ac0_dir = power_supply_dir.mkdir("BAT2")
    ac0_dir.join("type").write("Sector")

    monkeypatch.setattr(barython.widgets.battery, "BAT_DIR",
                        str(power_supply_dir))
    return power_supply_dir


def test_battery_widget_list_batteries(one_battery_dir):
    bw = BatteryWidget()
    assert list(bw.list_batteries()) == ["BAT0", ]


def test_battery_widget_list_batteries_multiple_bat(multiple_batteries_dir):
    bw = BatteryWidget()
    detected_batteries = list(bw.list_batteries())
    detected_batteries.sort()
    assert detected_batteries == ["BAT0", "BAT1"]


def test_battery_widget_read_battery_infos(one_battery_dir):
    BAT_NAME = "BAT0"
    bw = BatteryWidget()
    read_infos = bw.read_battery_infos(BAT_NAME)
    for key, expected_value in BATTERIES[BAT_NAME].items():
        assert read_infos[key] == expected_value

    expected_remains = (
        60 * BATTERIES[BAT_NAME]["energy_now"]/BATTERIES[BAT_NAME]["power_now"]
    )
    assert int(expected_remains) == read_infos["remains"]


def test_battery_widget_organize_result_one_battery(one_battery_dir):
    BAT_NAME = "BAT0"
    bw = BatteryWidget()
    infos = bw.read_battery_infos(BAT_NAME)
    expected = bw.organize_result(**{BAT_NAME: infos})
    assert expected == "{}% - 2:18".format(infos["capacity"])


def test_battery_widget_organize_result_multiple_batteries(
        multiple_batteries_dir):
    bw = BatteryWidget(padding=2)
    infos = {
        bat_name: bw.read_battery_infos(bat_name)
        for bat_name in BATTERIES.keys()
    }
    expected = bw.organize_result(**infos)
    assert expected == (
        "BAT0: {}% - 2:18".format(infos["BAT0"]["capacity"]) +
        "  "
        "BAT1: {}% - 1:19".format(infos["BAT1"]["capacity"])
    )


def test_battery_widget_update(one_battery_dir):
    BAT_NAME = "BAT0"
    bw = BatteryWidget()
    infos = bw.read_battery_infos(BAT_NAME)
    organized_result = bw.organize_result(**{BAT_NAME: infos})

    p = Panel(instance_per_screen=False, keep_unplugged_screens=True)
    s = Screen("HDMI-0")
    s.add_widget("l", bw)
    p.add_screen(s)
    bw.update()

    assert bw._content == organized_result
