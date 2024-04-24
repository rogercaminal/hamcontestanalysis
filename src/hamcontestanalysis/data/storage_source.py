"""HamContestAnalysis Storage Data Source class definition."""

import os
from abc import ABC
from os import PathLike
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union
from urllib.request import urlopen

from pandas import DataFrame
from pandas import read_csv
from pandas import read_parquet

from hamcontestanalysis.data.data_source import DataSource


class StorageDataSource(DataSource, ABC):
    """Storage Data Source abstract class.

    This abstract class defines a data source taken from local or remote storage, and
    defines its main interface and options.

    The class variables `file_format` and `path` determine how and where to push the
    data to, respectively. The `file_format` variable is a string which is mapped to the
    the read method to use via the `StorageDataSource.read_method_by_file_format`
    mapping.
    The `path` is a string or path-like object to specify data source path.
    This variable can be optionally prefixed as `{prefix}/{path}` if a `prefix` string
    is provided on instance constructor.
    The (prefixed) string could be a URL pointing to a local or remote storage, with
    valid URL schemes including http, ftp, s3, gs, and file.

    On data access, the class reads the desired source with format `file_format` from
    the specified `path`, local or remote, and passes the read data to the
    `process_result` method to perform processing operations, e.g. data type
    transforamtions, filtering, NaN filling, etc.

    The read method can be provided with additional keyword arguments via the
    `storage_options` class/instance variable.
    """

    file_format: ClassVar[str]
    path: ClassVar[Union[str, PathLike]]
    prefix: Optional[str]
    storage_options: ClassVar[Mapping[str, Any]] = {}
    supported_file_formats: ClassVar[List[str]] = ["csv", "parquet", "pickle"]
    read_method_by_file_format: ClassVar[Mapping[str, Callable[..., DataFrame]]] = {
        "csv": read_csv,
        "parquet": read_parquet,
    }

    def __init__(self, prefix: Optional[str] = None) -> None:
        """Storage Data Source constructor.

        Args:
            prefix: string with prefix to prepend the data source's path. Defaults to
                None to avoid prepending.
        """
        self.path = self.path if prefix is None else os.path.join(prefix, self.path)
        self.prefix = prefix

    def load(self) -> DataFrame:
        """Load data from storage.

        This method reads the data from the given storage path according to the
        specified file format and returns the read and processed dataframe.

        Returns:
            DataFrame loaded and processed.
        """
        data = self.read(
            file_format=self.file_format, path=self.path, **self.storage_options
        )
        return self.process_result(data=data)

    def process_result(self, data: DataFrame) -> DataFrame:
        """Process result from storage read."""
        return data

    def read(
        self,
        file_format: str,
        path: Union[str, PathLike],
        **kwargs: Any,
    ) -> DataFrame:
        """Read data from storage.

        This method selects a read method according to the given file format, specified
        in the `StorageDataSource.read_method_by_file_format` mapping, and reads the
        source's data from the given path. Additional keyword arguments are passed down
        to the read method. If no read method is set for the given file format, a
        NotImplementedError is raised.

        Args:
            file_format: string with format of the data source to read.
            path: string or os.PathLike with path of the data source to read.
            kwargs: any additional keyword arguments, passed down to the read method by
                format.

        Returns:
            Dataframe with data from storage.
        """
        if file_format not in self.read_method_by_file_format:
            raise NotImplementedError(
                f"Reading from format {self.file_format} not implemented."
            )
        read_method = self.read_method_by_file_format[file_format]
        return read_method(path, **kwargs)

    @staticmethod
    def _download_raw_data(website_address):
        with urlopen(website_address) as response:
            html = response.read().decode("unicode_escape")
        return html
