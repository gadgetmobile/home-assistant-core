"""PyTest fixtures and test helpers."""

from unittest import mock

from asynctest import CoroutineMock, call, patch
import blebox_uniapi
import pytest

from homeassistant.components.blebox import const
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import ConfigEntryNotReady

from tests.common import MockConfigEntry


def setup_product_mock(
    category, feature_mocks, path="homeassistant.components.blebox.Products"
):
    """Mock a product returning the given features."""

    product_mock = mock.create_autospec(
        blebox_uniapi.box.Box, True, True, features={category: feature_mocks}
    )
    patcher = patch(path, mock.DEFAULT, blebox_uniapi.products.Products, True, True)
    products_class = patcher.start()
    products_class.async_from_host = CoroutineMock(return_value=product_mock)
    return product_mock


def mock_only_feature(spec, **kwargs):
    """Mock just the feature, without the product setup."""
    return mock.create_autospec(spec, True, True, **kwargs)


def mock_feature(category, spec, **kwargs):
    """Mock a feature along with whole product setup."""
    feature_mock = mock_only_feature(spec, **kwargs)
    setup_product_mock(category, [feature_mock])
    return feature_mock


def mock_config(ip_address="172.100.123.4"):
    """Return a Mock of the HA entity config."""
    return MockConfigEntry(
        domain=const.DOMAIN, data={CONF_HOST: ip_address, CONF_PORT: 80},
    )


class DefaultBoxTest:
    """Base class with methods common to BleBox integration tests."""

    IP = "172.0.0.1"
    HASS_TYPE = None  # Must be set in subclass

    async def async_mock_entities(self, hass):
        """Return a new entities configured through HASS."""

        config = mock_config(self.IP)
        config.add_to_hass(hass)

        mod = self.HASS_TYPE

        all_entries = []

        def add_entries(entries, update):
            for entry in entries:
                entry.hass = hass
                all_entries.append(entry)

        assert await mod.async_setup_entry(hass, config, add_entries) is True
        return all_entries

    async def async_updated_entity(self, hass, index):
        """Return an already-updated entity created through HASS."""
        entity = (await self.async_mock_entities(hass))[index]
        await entity.async_update()
        return entity

    async def test_setup_failure(self, hass):
        """Mock the Product class."""

        path = "homeassistant.components.blebox.Products"
        patcher = patch(path, mock.DEFAULT, blebox_uniapi.products.Products, True, True)
        products_class = patcher.start()

        products_class.async_from_host = CoroutineMock(
            side_effect=blebox_uniapi.error.ClientError
        )

        with patch("homeassistant.components.blebox._LOGGER.error") as error:
            with pytest.raises(ConfigEntryNotReady):
                await self.async_mock_entities(hass)

            error.assert_has_calls(
                [
                    call(
                        "Failed to add/identify device at %s:%d (%s)",
                        "172.0.0.1",
                        80,
                        mock.ANY,
                    )
                ]
            )
            assert isinstance(error.call_args[0][3], blebox_uniapi.error.ClientError)
