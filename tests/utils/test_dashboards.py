"""Test utils.calculation.contests."""

from typing import Tuple

import dash
import pytest
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from pydantic.error_wrappers import ValidationError

from hamcontestanalysis.utils.dashboards.callbacks_manager import Callback
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager


@pytest.fixture
def callback_object():
    co = Callback(
        func=lambda x: x,
        inputs=Input("", ""),
        outputs=Output("", ""),
        states=State("", ""),
    )
    return co


callback_manager = CallbackManager()
app = dash.Dash("test")


def test_callback_object(callback_object):
    assert isinstance(callback_object, Callback)


def test_type_error_callback_object():
    with pytest.raises(ValidationError):
        Callback(
            func=1,
            inputs=Input("", ""),
            outputs=Output("", ""),
            states=State("", ""),
        )
    with pytest.raises(ValidationError):
        Callback(
            func=lambda x: x,
            inputs=None,
            outputs=Output("", ""),
            states=State("", ""),
        )
    with pytest.raises(ValidationError):
        Callback(
            func=lambda x: x,
            inputs=Input("", ""),
            outputs=None,
            states=State("", ""),
        )
    with pytest.raises(ValidationError):
        Callback(
            func=lambda x: x,
            inputs=Input("", ""),
            outputs=Output("", ""),
            states=None,
        )


def test_callback_manager():
    # Define dummy functions with callback
    @callback_manager.callback(
        Output("output_argument", "output_property"),
        [
            Input("input_argument_1", "input_property_1"),
            Input("input_argument_2", "input_property_2"),
        ],
    )
    def dummy_function(a: str, b: str) -> Tuple[str, str]:
        return a, b

    assert isinstance(app._callback_list, list)
    assert len(app._callback_list) == 0

    callback_manager.attach_to_app(app=app)

    assert isinstance(app._callback_list, list)
    assert len(app._callback_list) == 1
    assert isinstance(app._callback_list[0], dict)
    assert app._callback_list[0]["output"] == "output_argument.output_property"
    assert isinstance(app._callback_list[0]["inputs"], list)
    assert len(app._callback_list[0]["inputs"]) == 2
    assert app._callback_list[0]["inputs"][0]["id"] == "input_argument_1"
    assert app._callback_list[0]["inputs"][0]["property"] == "input_property_1"
    assert app._callback_list[0]["inputs"][1]["id"] == "input_argument_2"
    assert app._callback_list[0]["inputs"][1]["property"] == "input_property_2"
