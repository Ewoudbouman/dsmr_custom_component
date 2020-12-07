"""Constants for the custom dsmr integration."""
from homeassistant.const import (
    ELECTRICAL_CURRENT_AMPERE,
    ENERGY_KILO_WATT_HOUR,
    POWER_KILO_WATT,
    VOLT,
    VOLUME_CUBIC_METERS,
)

DOMAIN = "custom_dsmr"
PLATFORMS = ["sensor"]
API_V1_ACTUAL = "/api/v1/sm/actual"
API_V1_HIST_HOURS = "/api/v1/hist/hours"
API_V1_HIST_DAYS = "/api/v1/hist/days"
API_V1_HIST_MONTHS = "/api/v1/hist/months"
CONF_HISTORY_HOUR = "history_hour"
CONF_HISTORY_DAY = "history_day"
CONF_HISTORY_MONTH = "history_month"

SENSOR_FORMAT = {
    "energy_delivered_tariff1": {
        "name": "energy delivered tariff1",
        "unit": ENERGY_KILO_WATT_HOUR,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "energy_delivered_tariff2": {
        "name": "energy deliveredtariff2",
        "unit": ENERGY_KILO_WATT_HOUR,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "energy_hours_delivered_0": {
        "name": "energy hours delivered 0",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "hours",
    },
    "energy_hours_delivered_1": {
        "name": "energy hours delivered 1",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "hours",
    },
    "energy_days_delivered_0": {
        "name": "energy days delivered 0",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "days",
    },
    "energy_days_delivered_1": {
        "name": "energy days delivered 1",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "months",
    },
    "energy_months_delivered_0": {
        "name": "energy months delivered 0",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "months",
    },
    "energy_months_delivered_1": {
        "name": "energy months delivered 1",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "months",
    },
    "energy_returned_tariff1": {
        "name": "energy returned tariff 1",
        "unit": ENERGY_KILO_WATT_HOUR,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "energy_returned_tariff2": {
        "name": "energy returned tariff 2",
        "unit": ENERGY_KILO_WATT_HOUR,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "energy_hours_returned_0": {
        "name": "energy hours returned 0",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "hours",
    },
    "energy_hours_returned_1": {
        "name": "energy hours returned 1",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "hours",
    },
    "energy_days_returned_0": {
        "name": "energy days returned 0",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "days",
    },
    "energy_days_returned_1": {
        "name": "energy days returned 1",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "days",
    },
    "energy_months_returned_0": {
        "name": "energy months returned 0",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "months",
    },
    "energy_months_returned_1": {
        "name": "energy months returned 1",
        "unit": ENERGY_KILO_WATT_HOUR,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "",
    },
    "power_delivered": {
        "name": "power delivered",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "power_returned": {
        "name": "power returned",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "voltage_l1": {
        "name": "voltage l1",
        "unit": VOLT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "current_l1": {
        "name": "current l1",
        "unit": ELECTRICAL_CURRENT_AMPERE,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "power_delivered_l1": {
        "name": "power delivered l1",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "power_returned_l1": {
        "name": "power returned l1",
        "unit": POWER_KILO_WATT,
        "icon": "mdi:flash",
        "utility": "energy",
        "period": "actual",
    },
    "gas_delivered": {
        "name": "Gas delivered",
        "unit": VOLUME_CUBIC_METERS,
        "icon": "mdi:gas",
        "utility": "gas",
        "period": "actual",
    },
    "gas_hours_delivered_0": {
        "name": "gas hours delivered 0",
        "unit": VOLUME_CUBIC_METERS,
        "icon": "mdi:gas",
        "utility": "gas",
        "period": "hours",
    },
    "gas_hours_delivered_1": {
        "name": "gas hours delivered 1",
        "unit": VOLUME_CUBIC_METERS,
        "icon": "mdi:gas",
        "utility": "gas",
        "period": "hours",
    },
    "gas_days_delivered_0": {
        "name": "gas days delivered 0",
        "unit": VOLUME_CUBIC_METERS,
        "icon": "mdi:gas",
        "utility": "gas",
        "period": "days",
    },
    "gas_days_delivered_1": {
        "name": "gas days delivered 1",
        "unit": VOLUME_CUBIC_METERS,
        "icon": "mdi:gas",
        "utility": "gas",
        "period": "days",
    },
    "gas_months_delivered_0": {
        "name": "gas months delivered 0",
        "unit": VOLUME_CUBIC_METERS,
        "icon": "mdi:gas",
        "utility": "gas",
        "period": "months",
    },
    "gas_months_delivered_1": {
        "name": "gas months delivered 1",
        "unit": VOLUME_CUBIC_METERS,
        "icon": "mdi:gas",
        "utility": "gas",
        "period": "months",
    },
}