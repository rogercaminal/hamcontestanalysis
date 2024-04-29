# Usage

`hamcontestanalysis` comprises a set of tools for radio amateurs dedicated to analyze
contest with the maximum detail.

When installed, a full CLI is made available. This library has been structured into
different modules as shown below, that provide the user with different capabilities:

```{eval-rst}
.. typer:: hamcontestanalysis.cli:app
    :prog: hamcontestanalysis
```

In the following, the different modules will be described.

## Dashboard

The dashboard can be run locally with the `hamcontestanalysis dashboard` command.
There is currently one single dashboard (`contest-analysis`), but the package is
prepared to easily add more if needed.

To run the contest analysis dashboard locally, type

```
hamcontestanalysis dashboard contest-analysis
```

The dashboard is shown in http://localhost:8050, although both the address and port
can be easily changed with the appropiate call:

```{eval-rst}
.. typer:: hamcontestanalysis.cli.dashboard:app
    :prog: hamcontestanalysis dashboard
```

## Download

Logs from any supported contest can be downloaded locally with the
`hamcontestanalysis download` command. This command is automatically run when
analysing a contest with a dashboard. However, this command is provided separately in
case further independent analysis wants to be performed.

The downloading directory can be defined by setting the appropriate environment variable:

```bash
export HAMCONTESTANALYSISSTORAGE=/Users/my/folder/for/this/app
```

The following command downloads the desired log and stores it in `parquet` format.

```{eval-rst}
.. typer:: hamcontestanalysis.cli.download:app
    :prog: hamcontestanalysis download main
```

## Plots

The different plots shown in the dashboard can also be produced and stored locally in
`html` format, with the `plot` command.

The storage directory of the plots can be defined by setting the appropriate
environment variable:

```bash
export HAMCONTESTANALYSISPLOTS=/Users/my/folder/for/the/plots
```

```{eval-rst}
.. typer:: hamcontestanalysis.cli.plot:app
    :prog: hamcontestanalysis plot
```

Each of the plots can have different arguments, that can be visualized with the option
`--help`.

## Library

The `hamcontestanalysis` package can also be used as a library. Below are
examples with some useful code snippets:

### Load data

Contest data
There are currently four contests supported: CQ WW (cqww), CQ WPX (cqwpx), IARU HF (iaru), and ARRL DX (arrldx). The following command shows how to load the data for a particular contest, year, mode and callsign into a pandas data frame.

```python
from hamcontestanalysis.data.cqww.storage_source import CabrilloDataSource

data = CabrilloDataSource(callsign="EF6T", year="2023", mode="cw").load()
```

A list with all the available call signs per contest, year, and category can be obtained with the following command:

```python
from hamcontestanalysis.data.cqww.storage_source import CabrilloDataSource

list_of_callsigns = CabrilloDataSource._get_available_callsigns(year=2023, mode="cw")
```

### RBN data

Reverse Beacon data (RBN) can be loaded with the following command, either for a certain contest (only those supported), or for a custom date.

```python
from datetime import date
from hamcontestanalysis.data.rbn.storage_source import ReverseBeaconRawDataSource

data_from_custom_date = ReverseBeaconRawDataSource(year=2024, mode="cw", dates=[date(2024, 4, 23)]).load()
data_from_contest = ReverseBeaconRawDataSource(year=2023, mode="cw", contest="cqww").load()
```
