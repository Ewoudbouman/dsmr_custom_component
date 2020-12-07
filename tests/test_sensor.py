"""Tests for the dsmr sensors. Includes tests for message parsing and sensor updates."""
from homeassistant.components.custom_dsmr.const import (API_V1_ACTUAL,
                                                        API_V1_HIST_DAYS,
                                                        API_V1_HIST_HOURS,
                                                        API_V1_HIST_MONTHS)
from homeassistant.components.custom_dsmr.sensor import (DSMRHistData,
                                                         DSMRLiveData,
                                                         DSMRSensor)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from tests.async_mock import AsyncMock
from tests.common import MockConfigEntry

dsmr_live_json = {
    "actual": [
        {"name": "timestamp", "value": "201207113025W"},
        {"name": "energy_delivered_tariff1", "value": 10497.653, "unit": "kWh"},
        {"name": "energy_delivered_tariff2", "value": 11101.499, "unit": "kWh"},
        {"name": "energy_returned_tariff1", "value": 1078.85, "unit": "kWh"},
        {"name": "energy_returned_tariff2", "value": 2320.433, "unit": "kWh"},
        {"name": "power_delivered", "value": 3.264, "unit": "kW"},
        {"name": "power_returned", "value": 0.0, "unit": "kW"},
        {"name": "voltage_l1", "value": 227.3, "unit": "V"},
        {"name": "current_l1", "value": 14, "unit": "A"},
        {"name": "power_delivered_l1", "value": 3.24, "unit": "kW"},
        {"name": "power_returned_l1", "value": 0.0, "unit": "kW"},
        {"name": "gas_delivered", "value": 4394.229, "unit": "m3"},
    ]
}

dsmr_live_parsed = {
    "timestamp": {"value": "201207113025W"},
    "energy_delivered_tariff1": {"value": 10497.653, "unit": "kWh"},
    "energy_delivered_tariff2": {"value": 11101.499, "unit": "kWh"},
    "energy_returned_tariff1": {"value": 1078.85, "unit": "kWh"},
    "energy_returned_tariff2": {"value": 2320.433, "unit": "kWh"},
    "power_delivered": {"value": 3.264, "unit": "kW"},
    "power_returned": {"value": 0.0, "unit": "kW"},
    "voltage_l1": {"value": 227.3, "unit": "V"},
    "current_l1": {"value": 14, "unit": "A"},
    "power_delivered_l1": {"value": 3.24, "unit": "kW"},
    "power_returned_l1": {"value": 0.0, "unit": "kW"},
    "gas_delivered": {"value": 4394.229, "unit": "m3"},
}

dsmr_hist_hour_json = {
    "hours": [
        {
            "recnr": 0,
            "recid": "20120711",
            "slot": 44,
            "edt1": 10497.653,
            "edt2": 11102.047,
            "ert1": 1078.85,
            "ert2": 2320.433,
            "gdt": 4394.55,
        },
        {
            "recnr": 1,
            "recid": "20120710",
            "slot": 43,
            "edt1": 10497.653,
            "edt2": 11101.311,
            "ert1": 1078.85,
            "ert2": 2320.432,
            "gdt": 4394.23,
        },
        {
            "recnr": 2,
            "recid": "20120709",
            "slot": 42,
            "edt1": 10497.653,
            "edt2": 11100.86,
            "ert1": 1078.85,
            "ert2": 2320.432,
            "gdt": 4394.212,
        },
    ]
}

dsmr_hist_hour_parsed = {
    "energy_hours_delivered_0": 0.7360000000007858,
    "energy_hours_returned_0": 0.0010000000002037268,
    "gas_hours_delivered_0": 0.32000000000061846,
    "energy_hours_delivered_1": 0.4510000000009313,
    "energy_hours_returned_1": 0.0,
    "gas_hours_delivered_1": 0.01799999999911961,
}

dsmr_hist_day_json = {
    "days": [
        {
            "recnr": 0,
            "recid": "20120711",
            "slot": 3,
            "edt1": 10497.653,
            "edt2": 11102.047,
            "ert1": 1078.85,
            "ert2": 2320.433,
            "gdt": 4394.55,
        },
        {
            "recnr": 1,
            "recid": "20120623",
            "slot": 2,
            "edt1": 10495.325,
            "edt2": 11099.125,
            "ert1": 1078.85,
            "ert2": 2320.432,
            "gdt": 4394.058,
        },
        {
            "recnr": 2,
            "recid": "20120523",
            "slot": 1,
            "edt1": 10481.064,
            "edt2": 11099.125,
            "ert1": 1078.713,
            "ert2": 2320.432,
            "gdt": 4387.364,
        },
    ]
}

dsmr_hist_day_parsed = {
    "energy_days_delivered_0": 5.25,
    "energy_days_returned_0": 0.0010000000002037268,
    "gas_days_delivered_0": 0.4920000000001892,
    "energy_days_delivered_1": 14.261000000002241,
    "energy_days_returned_1": 0.13700000000017099,
    "gas_days_delivered_1": 6.694000000000415,
}

dsrm_hist_month_json = {
    "months": [
        {
            "recnr": 0,
            "recid": "20120711",
            "slot": 15,
            "edt1": 10497.653,
            "edt2": 11102.047,
            "ert1": 1078.85,
            "ert2": 2320.433,
            "gdt": 4394.55,
        },
        {
            "recnr": 1,
            "recid": "20113023",
            "slot": 14,
            "edt1": 10458.14,
            "edt2": 11051.787,
            "ert1": 1078.191,
            "ert2": 2320.158,
            "gdt": 4363.329,
        },
        {
            "recnr": 2,
            "recid": "20103123",
            "slot": 13,
            "edt1": 10264.634,
            "edt2": 10830.022,
            "ert1": 1072.049,
            "ert2": 2302.432,
            "gdt": 4272.227,
        },
    ]
}

dsmr_hist_month_parsed = {
    "energy_months_delivered_0": 89.77300000000105,
    "energy_months_returned_0": 0.9339999999997417,
    "gas_months_delivered_0": 31.22100000000046,
    "energy_months_delivered_1": 415.270999999997,
    "energy_months_returned_1": 23.868000000000393,
    "gas_months_delivered_1": 91.10199999999986,
}

dsmr_formatted_hours_response = {
    "energy_hours_delivered_0": 0.19700000000011642,
    "energy_hours_returned_0": 0.0,
    "gas_hours_delivered_0": 0.0,
    "energy_hours_delivered_1": 0.6169999999983702,
    "energy_hours_returned_1": 0.0,
    "gas_hours_delivered_1": 0.07999999999992724,
}

dsmr_formatted_days_response = {
    "energy_days_delivered_0": 14.0,
    "energy_days_returned_0": 0.13700000000017099,
    "gas_days_delivered_0": 6.694000000000415,
    "energy_days_delivered_1": 12.104999999995925,
    "energy_days_returned_1": 0.5219999999999345,
    "gas_days_delivered_1": 5.802999999999884,
}

dsmr_formatted_months_response = {
    "energy_months_delivered_0": 84.2619999999988,
    "energy_months_returned_0": 0.932999999999538,
    "gas_months_delivered_0": 30.72900000000027,
    "energy_months_delivered_1": 415.270999999997,
    "energy_months_returned_1": 23.868000000000393,
    "gas_months_delivered_1": 91.10199999999986,
}


async def test_parse_live_data(hass):
    """Test if the received live message gets parsed correctly."""
    session = async_get_clientsession(hass)
    live_data = DSMRLiveData(session, None)

    assert live_data.data is None
    bad_response = {}
    live_data.parse_live_data(bad_response)
    assert live_data.data is None
    live_data.parse_live_data(dsmr_live_json)
    assert live_data.data == dsmr_live_parsed


async def test_parse_historical_data_hour(hass):
    """Test if the received historical hour message gets parsed correctly."""
    session = async_get_clientsession(hass)
    hour_data = DSMRHistData(session, None, "hours")
    assert hour_data.data is None
    bad_response = {}
    hour_data.parse_historical_data(bad_response)
    assert hour_data.data is None
    hour_data.parse_historical_data(dsmr_hist_hour_json)
    assert hour_data.data == dsmr_hist_hour_parsed


async def test_parse_historical_data_day(hass):
    """Test if the received historical day message gets parsed correctly."""
    session = async_get_clientsession(hass)
    day_data = DSMRHistData(session, None, "days")
    assert day_data.data is None
    bad_response = {}
    day_data.parse_historical_data(bad_response)
    assert day_data.data is None
    day_data.parse_historical_data(dsmr_hist_day_json)
    assert day_data.data == dsmr_hist_day_parsed


async def test_parse_historical_data_month(hass):
    """Test if the received historical months message gets parsed correctly."""
    session = async_get_clientsession(hass)
    month_data = DSMRHistData(session, None, "months")
    assert month_data.data is None
    bad_response = {}
    month_data.parse_historical_data(bad_response)
    assert month_data.data is None
    month_data.parse_historical_data(dsrm_hist_month_json)
    assert month_data.data == dsmr_hist_month_parsed


async def test_default_setup(hass):
    """Test if only the live sensors are initialized during setup."""
    entry_data = {
        "host": "http://192.168.1.121",
        "history_hour": False,
        "history_day": False,
        "history_month": False,
    }
    mock_entry = MockConfigEntry(domain="custom_dsmr", data=entry_data)
    mock_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()
    await hass.helpers.entity_registry.async_get_registry()
    power_delivered = hass.states.get("sensor.power_delivered")
    assert power_delivered.state == "unknown"

    gas_hours_delivered_0 = hass.states.get("sensor.gas_hours_delivered_0")
    assert gas_hours_delivered_0 is None


async def test_actual_and_hour_setup(hass):
    """Test if the live and hourly sensors are initialized during setup."""
    entry_data = {
        "host": "http://192.168.1.121",
        "history_hour": True,
        "history_day": False,
        "history_month": False,
    }
    mock_entry = MockConfigEntry(domain="custom_dsmr", data=entry_data)
    mock_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()
    await hass.helpers.entity_registry.async_get_registry()
    power_delivered = hass.states.get("sensor.power_delivered")
    assert power_delivered.state == "unknown"
    gas_hours_delivered_0 = hass.states.get("sensor.gas_hours_delivered_0")
    assert gas_hours_delivered_0.state == "unknown"


async def test_actual_and_all_history_setup(hass):
    """Test if all sensors are initialized during setup."""
    entry_data = {
        "host": "http://192.168.1.121",
        "history_hour": True,
        "history_day": True,
        "history_month": True,
    }
    mock_entry = MockConfigEntry(domain="custom_dsmr", data=entry_data)
    mock_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()
    await hass.helpers.entity_registry.async_get_registry()
    power_delivered = hass.states.get("sensor.power_delivered")
    assert power_delivered.state == "unknown"
    gas_hours_delivered_0 = hass.states.get("sensor.gas_hours_delivered_0")
    assert gas_hours_delivered_0.state == "unknown"
    gas_days_delivered_0 = hass.states.get("sensor.gas_days_delivered_0")
    assert gas_days_delivered_0.state == "unknown"
    gas_months_delivered_0 = hass.states.get("sensor.gas_months_delivered_0")
    assert gas_months_delivered_0.state == "unknown"


async def test_dsmr_live_sensor(hass):
    """Test if the live sensor updates."""
    session = async_get_clientsession(hass)
    data = DSMRLiveData(session, "1.2.3.4")
    data.async_update = AsyncMock(return_value=dsmr_live_parsed)
    entity = DSMRSensor("energy_delivered_tariff1", data)
    assert entity.state is None
    assert data.latest_data("energy_delivered_tariff1") is None
    data._data = await data.async_update()  # pylint: disable=protected-access
    assert data.data is dsmr_live_parsed
    assert data.latest_data("energy_delivered_tariff1") == 10497.653


async def test_dsmr_live_data(hass):
    """Test if the live data class behaves correctly when handling data."""
    api = "http://192.168.1.121" + API_V1_ACTUAL
    session = async_get_clientsession(hass)
    data = DSMRLiveData(session, api)
    data.async_update = AsyncMock(return_value=dsmr_live_parsed)
    assert data.api is api
    assert data.data is None
    data._data = await data.async_update()  # pylint: disable=protected-access
    assert data.data is not None
    assert data.latest_data("energy_delivered_tariff1") == 10497.653


async def test_dsmr_hist_data_hours(hass):
    """Test if the historical hour data class behaves correctly when handling data."""
    session = async_get_clientsession(hass)
    api = "http://192.168.1.121" + API_V1_HIST_HOURS
    data = DSMRHistData(session, api, "hours")
    data.async_update = AsyncMock(return_value=dsmr_formatted_hours_response)
    assert data.api is api
    assert data.data is None
    data._data = await data.async_update()  # pylint: disable=protected-access
    assert data.data is not None
    assert data.data["gas_hours_delivered_0"] == 0.0


async def test_dsmr_hist_data_days(hass):
    """Test if the historical day data class behaves correctly when handling data."""
    session = async_get_clientsession(hass)
    api = "http://192.168.1.121" + API_V1_HIST_DAYS
    data = DSMRHistData(session, api, "days")
    data.async_update = AsyncMock(return_value=dsmr_formatted_days_response)
    assert data.api is api
    assert data.data is None
    data._data = await data.async_update()  # pylint: disable=protected-access
    assert data.data is not None
    assert data.data["gas_days_delivered_0"] == 6.694000000000415


async def test_dsmr_hist_data_months(hass):
    """Test if the historical month data class behaves correctly when handling data."""
    session = async_get_clientsession(hass)
    api = "http://192.168.1.121" + API_V1_HIST_MONTHS
    data = DSMRHistData(session, api, "months")
    data.async_update = AsyncMock(return_value=dsmr_formatted_months_response)
    assert data.api is api
    assert data.data is None
    data._data = await data.async_update()  # pylint: disable=protected-access
    assert data.data is not None
    assert data.data["gas_months_delivered_0"] == 30.72900000000027
