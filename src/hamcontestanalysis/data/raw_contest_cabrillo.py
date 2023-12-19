"""Contest cabrillo data source module."""
import re
from collections import defaultdict
from io import StringIO
from os import PathLike
from typing import Any
from typing import ClassVar
from typing import Optional
from typing import Union
from urllib.request import urlopen

from pandas import DataFrame

from hamcontestanalysis.data.storage_source import StorageDataSource


class RawContestCabrilloDataSource(StorageDataSource):
    """Contest cabrillo data source definition."""

    file_format: ClassVar[str] = "csv"
    storage_options: ClassVar[dict] = {
        "header": None,
        "dtype": defaultdict(lambda: str),
    }
    path: ClassVar[Union[str, PathLike]]
    prefix: Optional[str]
    website_address_template: str

    def __init__(
        self,
        callsign: str,
        year: int,
        mode: str,
    ):
        """Raw contest cabrillo data source constructor.

        The constructor can be provided with optional values to filter loaded data, such
        as geographic granularity and prediciton model (name), either a single value or
        a list. In addition, the prefix to prepend the data source path is passed to
        the parent class StorageDataSource constructor.

        Args:
            callsign (str): Callsign to consider
            year (int): Year of the contest
            mode (str): Mode of the contest
        """
        self.path = self.path.format(
            callsign=callsign.lower(), year=year, mode=mode.lower()
        )
        super().__init__(prefix=self.prefix)
        self.callsign = callsign
        self.year = year
        self.mode = mode

    def read(
        self,
        file_format: str,
        path: Union[str, PathLike],
        **kwargs: Any,
    ) -> DataFrame:
        """Read data from contest website."""
        if file_format not in self.read_method_by_file_format:
            raise NotImplementedError(
                f"Reading from format {self.file_format} not implemented."
            )
        read_method = self.read_method_by_file_format[file_format]

        # Get text from web
        with urlopen(path) as response:
            html = response.read()
        csv = "\n".join(
            re.findall(
                r"\nQSO:,+(.+)",
                re.sub("[ \t\r\f\v]+", ",", html.decode("unicode_escape")),
            )
        )

        # Create dataframe
        _df = read_method(StringIO(csv), **kwargs)

        # metadata
        meta = [
            line
            for line in html.decode("unicode_escape").split("\n")
            if "QSO:" not in line
        ]
        for m in meta:
            try:
                k, v = m.split(": ")
            except ValueError:
                continue
            _df.attrs[k] = v
        return _df
