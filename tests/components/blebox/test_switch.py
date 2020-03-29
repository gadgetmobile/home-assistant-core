"""Blebox switch tests."""

from asynctest import CoroutineMock, PropertyMock
import blebox_uniapi
import pytest

from homeassistant.components.blebox import switch
from homeassistant.components.switch import DEVICE_CLASS_SWITCH

from .conftest import (
    DefaultBoxTest,
    mock_feature,
    mock_only_feature,
    setup_product_mock,
)


class TestSwitchBox(DefaultBoxTest):
    """Tests for BleBox switchBox."""

    def default_mock(self):
        """Return a default switchBox switch entity mock."""
        feature = mock_feature(
            "switches",
            blebox_uniapi.switch.Switch,
            unique_id="BleBox-switchBox-1afe34e750b8-0.relay",
            full_name="switchBox-0.relay",
            device_class="relay",
            is_on=False,
        )
        product = feature.product
        type(product).name = PropertyMock(return_value="My switch box")
        type(product).model = PropertyMock(return_value="switchBox")
        return feature

    @pytest.fixture(autouse=True)
    def feature_mock(self):
        """Return a mocked Switch feature representing a switchBox."""
        self._feature_mock = self.default_mock()
        return self._feature_mock

    HASS_TYPE = switch

    async def test_init(self, hass):
        """Test switch default state."""

        entity = (await self.async_mock_entities(hass))[0]

        assert entity.name == "switchBox-0.relay"
        assert entity.unique_id == "BleBox-switchBox-1afe34e750b8-0.relay"

        assert entity.device_class == DEVICE_CLASS_SWITCH

        assert entity.is_on is False  # state already available here

    async def test_device_info(self, hass, feature_mock):
        """Test device info."""
        entity = (await self.async_mock_entities(hass))[0]
        info = entity.device_info
        assert info["name"] == "My switch box"
        assert info["identifiers"] == {("blebox", "abcd0123ef5678")}
        assert info["manufacturer"] == "BleBox"
        assert info["model"] == "switchBox"
        assert info["sw_version"] == "1.23"

    def updateable_feature_mock(self):
        """Set up a mocked feature which can be updated."""
        feature_mock = self._feature_mock

        def update():
            feature_mock.is_on = False

        feature_mock.async_update = CoroutineMock(side_effect=update)

    async def test_update_when_off(self, hass, aioclient_mock):
        """Test switch updating when off."""

        self.updateable_feature_mock()

        entity = await self.async_updated_entity(hass, 0)

        assert entity.is_on is False

    def on_feature_mock(self):
        """Set up a mocked feature which can be updated."""
        feature_mock = self._feature_mock

        def update():
            feature_mock.is_on = True

        feature_mock.async_update = CoroutineMock(side_effect=update)

    async def test_update_when_on(self, hass, aioclient_mock):
        """Test switch updating when on."""

        self.on_feature_mock()

        entity = await self.async_updated_entity(hass, 0)
        assert entity.is_on is True

    def off_to_on_feature_mock(self):
        """Set up a mocked feature which can be updated and turned on."""
        feature_mock = self._feature_mock

        def update():
            feature_mock.is_on = False

        def turn_on():
            feature_mock.is_on = True

        feature_mock.async_update = CoroutineMock(side_effect=update)
        feature_mock.async_turn_on = CoroutineMock(side_effect=turn_on)

    async def test_on(self, hass, aioclient_mock):
        """Test turning switch on."""

        self.off_to_on_feature_mock()

        entity = await self.async_updated_entity(hass, 0)
        await entity.async_turn_on()
        assert entity.is_on is True

    def on_to_off_feature_mock(self):
        """Set up a mocked feature which can be updated and turned off."""
        feature_mock = self._feature_mock

        def update():
            feature_mock.is_on = True

        def turn_off():
            feature_mock.is_on = False

        feature_mock.async_update = CoroutineMock(side_effect=update)
        feature_mock.async_turn_off = CoroutineMock(side_effect=turn_off)

    async def test_off(self, hass, aioclient_mock):
        """Test turning switch off."""

        self.on_to_off_feature_mock()

        entity = await self.async_updated_entity(hass, 0)

        await entity.async_turn_off()
        assert entity.is_on is False


class TestSwitchBoxD(DefaultBoxTest):
    """Tests for BleBox switchBoxD."""

    HASS_TYPE = switch

    def default_mock(self, id=0):
        """Provide a default single-feature mock for base class."""

        id = 0
        feature = mock_feature(
            "switches",
            blebox_uniapi.switch.Switch,
            unique_id=f"BleBox-switchBoxD-1afe34e750b8-{id}.relay",
            full_name=f"switchBoxD-{id}.relay",
            device_class="relay",
            is_on=None,
        )
        return feature

    def default_mock_relay(self, id=0):
        """Return a default switchBoxD switch entity mock."""
        return mock_only_feature(
            blebox_uniapi.switch.Switch,
            unique_id=f"BleBox-switchBoxD-1afe34e750b8-{id}.relay",
            full_name=f"switchBoxD-{id}.relay",
            device_class="relay",
            is_on=None,
        )

    @pytest.fixture(autouse=True)
    def feature_mock(self):
        """Set up two mocked Switch features representing a switchBoxD."""
        r1 = self.default_mock_relay(0)
        r2 = self.default_mock_relay(1)

        self._feature_mocks = [r1, r2]

        # TODO: pass product to features mocks instead
        product = setup_product_mock("switches", self._feature_mocks)

        type(product).name = PropertyMock(return_value="My relays")
        type(product).model = PropertyMock(return_value="switchBoxD")
        type(product).brand = PropertyMock(return_value="BleBox")
        type(product).firmware_version = PropertyMock(return_value="1.23")
        type(product).unique_id = PropertyMock(return_value="abcd0123ef5678")

        type(r1).product = product
        type(r2).product = product

        return self._feature_mocks

    async def test_init(self, hass):
        """Test switch default state."""

        entities = await self.async_mock_entities(hass)

        entity = entities[0]
        # TODO: include relay output names?
        assert entity.name == "switchBoxD-0.relay"
        assert entity.unique_id == "BleBox-switchBoxD-1afe34e750b8-0.relay"
        assert entity.device_class == DEVICE_CLASS_SWITCH
        assert entity.is_on is None

        entity = entities[1]
        assert entity.name == "switchBoxD-1.relay"
        assert entity.unique_id == "BleBox-switchBoxD-1afe34e750b8-1.relay"
        assert entity.device_class == DEVICE_CLASS_SWITCH
        assert entity.is_on is None

    async def test_device_info(self, hass, feature_mock):
        """Test device info."""
        entity = (await self.async_mock_entities(hass))[0]
        info = entity.device_info
        assert info["name"] == "My relays"
        assert info["identifiers"] == {("blebox", "abcd0123ef5678")}
        assert info["manufacturer"] == "BleBox"
        assert info["model"] == "switchBoxD"
        assert info["sw_version"] == "1.23"

        entity = (await self.async_mock_entities(hass))[1]
        info = entity.device_info
        assert info["name"] == "My relays"
        assert info["identifiers"] == {("blebox", "abcd0123ef5678")}
        assert info["manufacturer"] == "BleBox"
        assert info["model"] == "switchBoxD"
        assert info["sw_version"] == "1.23"

    def updateable_feature_mock(self):
        """Set up a mocked feature which can be updated."""
        feature_mocks = self._feature_mocks

        def update0():
            feature_mocks[0].is_on = False
            feature_mocks[1].is_on = False

        feature_mocks[0].async_update = CoroutineMock(side_effect=update0)

    async def test_update_when_off(self, hass):
        """Test switch updating when off."""

        self.updateable_feature_mock()

        entities = await self.async_mock_entities(hass)

        # updating any one is fine (since both call product.async_update)
        await entities[0].async_update()

        assert entities[0].is_on is False
        assert entities[1].is_on is False

    def second_off_feature_mock(self):
        """Set up mocked features which can be updated."""
        feature_mocks = self._feature_mocks

        def update0():
            feature_mocks[0].is_on = True
            feature_mocks[1].is_on = False

        feature_mocks[0].async_update = CoroutineMock(side_effect=update0)

    async def test_update_when_second_off(self, hass):
        """Test switch updating when off."""

        self.second_off_feature_mock()

        entities = await self.async_mock_entities(hass)

        # updating any one is fine
        await entities[0].async_update()

        assert entities[0].is_on is True
        assert entities[1].is_on is False

    def turn_first_on_feature_mock(self):
        """Set up mocked features where first can be updated and turned on."""
        feature_mocks = self._feature_mocks

        def update0():
            feature_mocks[0].is_on = False
            feature_mocks[1].is_on = False

        def turn_on0():
            feature_mocks[0].is_on = True

        feature_mocks[0].async_update = CoroutineMock(side_effect=update0)
        feature_mocks[0].async_turn_on = CoroutineMock(side_effect=turn_on0)

    async def test_turn_first_on(self, hass, aioclient_mock):
        """Test turning switch on."""

        self.turn_first_on_feature_mock()

        entities = await self.async_mock_entities(hass)
        await entities[0].async_update()

        await entities[0].async_turn_on()
        assert entities[0].is_on is True
        assert entities[1].is_on is False

    def turn_second_on_feature_mock(self):
        """Set up mocked features where second can be updated and turned on."""
        feature_mocks = self._feature_mocks

        def update0():
            feature_mocks[0].is_on = False
            feature_mocks[1].is_on = False

        def turn_on1():
            feature_mocks[1].is_on = True

        feature_mocks[0].async_update = CoroutineMock(side_effect=update0)
        feature_mocks[1].async_turn_on = CoroutineMock(side_effect=turn_on1)

    async def test_second_on(self, hass, aioclient_mock):
        """Test turning switch on."""

        self.turn_second_on_feature_mock()

        entities = await self.async_mock_entities(hass)
        await entities[0].async_update()

        await entities[1].async_turn_on()
        assert entities[0].is_on is False
        assert entities[1].is_on is True

    def turn_first_off_feature_mock(self):
        """Set up mocked features where first can be updated and turned off."""

        feature_mocks = self._feature_mocks

        def update_any():
            feature_mocks[0].is_on = True
            feature_mocks[1].is_on = True

        def turn_off0():
            feature_mocks[0].is_on = False

        feature_mocks[0].async_update = CoroutineMock(side_effect=update_any)
        feature_mocks[0].async_turn_off = CoroutineMock(side_effect=turn_off0)

    async def test_first_off(self, hass, aioclient_mock):
        """Test turning switch on."""

        self.turn_first_off_feature_mock()

        entities = await self.async_mock_entities(hass)

        await entities[0].async_update()

        await entities[0].async_turn_off()
        assert entities[0].is_on is False
        assert entities[1].is_on is True

    def turn_second_off_feature_mock(self):
        """Set up mocked features where second can be updated and turned off."""
        feature_mocks = self._feature_mocks

        def update_any():
            feature_mocks[0].is_on = True
            feature_mocks[1].is_on = True

        def turn_off1():
            feature_mocks[1].is_on = False

        feature_mocks[0].async_update = CoroutineMock(side_effect=update_any)
        feature_mocks[1].async_turn_off = CoroutineMock(side_effect=turn_off1)

    async def test_second_off(self, hass, aioclient_mock):
        """Test turning switch on."""

        self.turn_second_off_feature_mock()

        entities = await self.async_mock_entities(hass)

        await entities[0].async_update()

        await entities[1].async_turn_off()
        assert entities[0].is_on is True
        assert entities[1].is_on is False
