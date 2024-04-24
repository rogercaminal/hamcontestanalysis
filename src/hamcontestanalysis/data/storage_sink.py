"""HamContestAnalysis Storage Data Sink class definition."""

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

from pandas import DataFrame

from hamcontestanalysis.data.data_sink import DataSink


class StorageDataSink(DataSink, ABC):
    """Storage Data Sink abstract class.

    This abstract class defines a data sink which pushes data to a path in local or
    remote storage, and defines its main interface and options.

    The class variables `file_format` and `path` determine how and where to push the
    data to, respectively. The `file_format` variable is a string which is mapped to the
    save method to use via the `StorageDataSink.save_method_by_file_format` mapping.
    The `path` is a string or path-like object to specify data sink path.
    This variable can be optionally prefixed as `{prefix}/{path}` if a `prefix` string
    is provided on instance constructor.
    The (prefixed) string could be a URL pointing to a local or remote storage, with
    valid URL schemes including http, ftp, s3, gs, and file.

    On data pushing, the class takes some input data (as `pandas.DataFrame`) and passes
    it to a `prepare_output` method. This method can be used to prepare data output,
    such as fill NaNs, filter or partition rows. After the output data is prepared, it
    is passed to the `save` method, which retrieves the specific
    `pandas.DataFrame.to_{file_format}` method according to `file_format`, then saves
    the data to the sink's `path`.

    The save method can be provided with additional keyword arguments via the
    `storage_options` class/instance variable.
    """

    file_format: ClassVar[str]
    path: ClassVar[Union[str, PathLike]]
    prefix: Optional[str]
    storage_options: ClassVar[Mapping[str, Any]] = {}
    supported_file_formats: ClassVar[List[str]] = ["csv", "parquet", "pickle"]
    save_method_by_file_format: ClassVar[Mapping[str, Callable[..., DataFrame]]] = {
        "csv": "to_csv",
        "parquet": "to_parquet",
        "pickle": "to_pickle",
    }

    def __init__(self, prefix: Optional[str] = None) -> None:
        """Storage Data Sink constructor.

        Args:
            prefix: string with prefix to prepend the data sinks's path. Defaults to
                None to avoid prepending.
        """
        self.path = self.path if prefix is None else os.path.join(prefix, self.path)
        self.prefix = prefix

    def push(self, data: DataFrame) -> None:
        """Push data to storage.

        This method pushes the given DataFrame to the given storage path according to
        the specified file format.

        Args:
            data: pandas.DataFrame with data to sink to storage.
        """
        output_data = self.prepare_output(data=data)
        self._create_prefix_folder()
        self.save(
            data=output_data,
            file_format=self.file_format,
            path=self.path,
            **self.storage_options,
        )

    def prepare_output(self, data: DataFrame) -> DataFrame:
        """Prepare output to sink."""
        return data

    def save(
        self,
        data: DataFrame,
        file_format: str,
        path: Union[str, PathLike],
        **kwargs: Any,
    ) -> None:
        """Save data to sink.

        This method selects a save method according to the given file format, specified
        in the `StorageDataSink.save_method_by_file_format` mapping, and saves the given
        data to the given storage path. Additional keyword arguments are passed down to
        the save method. If no save method is set for the given file format, a
        NotImplementedError is raised.

        Args:
            data: pandas.DataFrame with data to sink to storage.
            file_format: string with format of the data source to read.
            path: string or os.PathLike with path of the data source to read.
            kwargs: any additional keyword arguments, passed down to the read method by
                format.
        """
        if file_format not in self.save_method_by_file_format:
            raise NotImplementedError(
                f"Saving to format {self.file_format} not implemented."
            )
        save_method = getattr(data, self.save_method_by_file_format[file_format])
        save_method(path, **kwargs)

    def _create_prefix_folder(self):
        if not os.path.exists(self.prefix):
            os.makedirs(self.prefix)
