"""Callbacks for the rbn statistics tab."""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from pandas import DataFrame

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import exists_rbn
from hamcontestanalysis.plots.rbn.plot_cw_speed import PlotCwSpeed
from hamcontestanalysis.plots.rbn.plot_number_rbn_spots import PlotNumberRbnSpots
from hamcontestanalysis.plots.rbn.plot_snr_band_continent import PlotSnrBandContinent
from hamcontestanalysis.utils import BANDMAP
from hamcontestanalysis.utils import CONTINENTS
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager
from hamcontestanalysis.utils.types.dataframe_types import fix_types_data_rbn


callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("ph_snr_band_continent", "children"),
    [
        Input("signal", "data"),
    ],
)
def option_snr_band_continent(signal):
    """Callback option for SNR band-continent plot."""
    return html.Div(
        [
            dcc.Checklist(
                id="cl_snr_band",
                options=list(BANDMAP.keys()),
                value=list(BANDMAP.keys()),
                inline=True,
            ),
            dcc.Checklist(
                id="cl_snr_rx_continent",
                options=CONTINENTS,
                value=CONTINENTS,
                inline=True,
            ),
            dcc.Dropdown(
                id="rb_snr_time_bin",
                options=[5, 10, 30, 60],
                value=10,
            ),
        ]
    )


@callback_manager.callback(
    Output("snr_band_continent", "children"),
    [
        Input("signal", "data"),
        Input("cl_snr_band", "value"),
        Input("cl_snr_rx_continent", "value"),
        Input("rb_snr_time_bin", "value"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_snr_band_continent(
    signal, bands, rx_continents, time_bin_size, contest, mode, callsigns_years
):
    """Generate Dash plot of SNR band-continent."""
    f_callsigns_years = []

    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists_rbn(year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate

    years = list({c[1] for c in f_callsigns_years})
    if len(years) > 1:
        raise dash.exceptions.PreventUpdate

    plot = PlotSnrBandContinent(
        contest=contest,
        mode=mode,
        callsigns=[c[0] for c in f_callsigns_years],
        year=years[0],
        rx_continents=rx_continents,
        bands=bands,
        time_bin_size=time_bin_size,
    )
    data = fix_types_data_rbn(data=DataFrame(signal["data_rbn"]))
    plot.data = data
    return dcc.Graph(figure=plot.plot(), style={"width": "70vw", "height": "90vh"})


@callback_manager.callback(
    Output("ph_rbn", "children"),
    [
        Input("signal", "data"),
    ],
)
def option_rbn_stats(signal):
    """Callback option for RBN stast plot."""
    return html.Div(
        [
            dcc.Dropdown(
                id="rb_rbn_feature",
                options=[
                    {"label": "Counts", "value": "counts"},
                    {"label": "CW speed", "value": "speed"},
                ],
                value="counts",
            ),
            dcc.Dropdown(
                id="rb_rbn_time_bin",
                options=[5, 15, 30, 60],
                value=60,
            ),
            dcc.Checklist(
                id="cl_rbn_band",
                options=list(BANDMAP.keys()),
                value=list(BANDMAP.keys()),
                inline=True,
            ),
            dcc.Checklist(
                id="cl_rbn_rx_continent",
                options=CONTINENTS,
                value=CONTINENTS,
                inline=True,
            ),
        ]
    )


@callback_manager.callback(
    Output("rbn_stats", "children"),
    [
        Input("signal", "data"),
        Input("rb_rbn_feature", "value"),
        Input("rb_rbn_time_bin", "value"),
        Input("cl_rbn_band", "value"),
        Input("cl_rbn_rx_continent", "value"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_rbn_stats(
    signal, feature, time_bin_size, bands, rx_continents, contest, mode, callsigns_years
):
    """Generate Dash RBN stats plot."""
    f_callsigns_years = []
    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists_rbn(year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate
    if feature == "speed":
        plot = PlotCwSpeed(
            contest=contest,
            mode=mode,
            bands=bands,
            callsigns_years=f_callsigns_years,
            time_bin_size=time_bin_size,
        )
    elif feature == "counts":
        plot = PlotNumberRbnSpots(
            contest=contest,
            mode=mode,
            bands=bands,
            callsigns_years=f_callsigns_years,
            time_bin_size=time_bin_size,
            rx_continents=rx_continents,
        )
    else:
        raise ValueError("Plot does not exist")
    data = fix_types_data_rbn(data=DataFrame(signal["data_rbn"]))
    plot.data = data
    n_bands = len(bands)
    return dcc.Graph(figure=plot.plot(), style={"height": f"{15 * n_bands}vh"})
