"""Test the custom dsmr config flow."""
from homeassistant import config_entries, setup
from homeassistant.components.custom_dsmr.config_flow import CannotConnect
from homeassistant.components.custom_dsmr.const import DOMAIN
from tests.async_mock import patch


async def test_show_user_form(hass) -> None:
    """Test that we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["step_id"] == "user"
    assert result["type"] == "form"
    assert result["errors"] == {}


async def test_form_cannot_connect(hass):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "homeassistant.components.custom_dsmr.config_flow.validate_input",
        side_effect=CannotConnect,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "history_hour": False,
                "history_day": False,
                "history_month": False,
            },
        )
    assert result["type"] == "form"
    assert result["errors"] == {"base": "cannot_connect"}


async def test_cannont_connect_form(hass):
    """Test the processing of a valid form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    with patch(
        "homeassistant.components.custom_dsmr.config_flow.DSMRSetup.check_host",
        return_value=True,
    ), patch(
        "homeassistant.components.custom_dsmr.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "history_hour": False,
                "history_day": False,
                "history_month": False,
            },
        )
        await hass.async_block_till_done()
    assert result["type"] == "create_entry"
    assert result["title"] == "custom_dsmr"
    assert len(mock_setup_entry.mock_calls) == 1
