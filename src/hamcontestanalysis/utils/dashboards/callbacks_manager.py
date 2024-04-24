"""Callback manager class definition."""

from dataclasses import dataclass
from dataclasses import field
from typing import Callable
from typing import List
from typing import Union

from dash import Dash
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash.dependencies import handle_callback_args


@dataclass
class Callback:
    """Data class for Callback."""

    func: Callable
    outputs: Union[Output, List[Output]]
    inputs: Union[Input, List[Input]]
    states: Union[State, List[State]] = field(default_factory=list)
    kwargs: dict = field(default_factory=lambda: {"prevent_initial_call": False})


class CallbackManager:
    """CallbackManager class."""

    def __init__(self):
        """Init method."""
        self._callbacks = []

    def callback(self, *args, **kwargs):
        """Callback decorator definition."""
        output, inputs, state, prevent_initial_call = handle_callback_args(args, kwargs)

        def wrapper(func):
            self._callbacks.append(
                Callback(
                    func,
                    output,
                    inputs,
                    state,
                    {"prevent_initial_call": prevent_initial_call},
                )
            )

        return wrapper

    def attach_to_app(self, app: Dash):
        """Attach callback to app.

        Args:
            app (Dash): Dash application
        """
        for callback in self._callbacks:
            app.callback(
                callback.outputs, callback.inputs, callback.states, **callback.kwargs
            )(callback.func)
