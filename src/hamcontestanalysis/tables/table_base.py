"""Base class for tables in the dashboards."""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from dash.dash_table import DataTable
from pandas import DataFrame


class TableBase:
    """Table base class.

    This class serves as a base interface for the different tables,
    It mainly defines the `TableBase.show` method as the
    way to create a plotly object, implemented by each table subclass.
    """

    def __init__(
        self,
        columns: List[Dict[str, str]],
        style_table: Optional[Dict[Any, Any]] = None,
        style_data: Optional[Dict[Any, Any]] = None,
        filter_action: str = "native",
        sort_action: str = "native",
    ):
        """Init method."""
        self._columns = columns
        self._style_table = style_table
        self._style_data = style_data
        self._filter_action = filter_action
        self._sort_action = sort_action
        self._data: DataFrame = None

    @property
    def columns(self):
        """Property of columns."""
        if not isinstance(self._columns, list):
            raise TypeError("columns must be a list of dictionaries.")
        if not all([isinstance(d, dict) for d in self._columns]):
            raise TypeError("columns must be a list of dictionaries.")
        if not all([k in ("name", "id", "type") for k in self._columns[0].keys()]):
            raise ValueError(
                "The keys of each dictionary must be 'name', 'id', and 'type'"
            )
        if not all(
            [d["type"] in ("numeric", "text", "datetime") for d in self._columns]
        ):
            raise ValueError(
                "The values of type must be 'numeric', 'text' or 'datetime'."
            )
        return self._columns

    @property
    def style_table(self):
        """Property of style_table."""
        if self._style_table is None:
            return {"height": "300px", "overflowY": "auto"}
        return self._style_table

    @property
    def style_data(self):
        """Property of style_data."""
        if self._style_data is None:
            return {
                "width": "150px",
                "minWidth": "150px",
                "maxWidth": "150px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            }
        return self._style_data

    @property
    def filter_action(self):
        """Property of filter_action."""
        if self._filter_action not in ("native", "custom"):
            raise ValueError("filter_action must be 'native' or 'custom'")
        return self._filter_action

    @property
    def sort_action(self):
        """Property of sort_action."""
        if self._sort_action not in ("native", "custom"):
            raise ValueError("sort_action must be 'native' or 'custom'")
        return self._sort_action

    @property
    def data(self):
        """Property of attribute data."""
        if not isinstance(self._data, DataFrame):
            self._data = DataFrame()
        return self._data

    @data.setter
    def data(self, value):
        """Setter for the data attribute."""
        if not isinstance(value, DataFrame):
            raise TypeError("data must be a Pandas DataFrame")
        self._data = value

    def _filter_data(self) -> DataFrame:
        """Filter dataframe with the data to be contained in the table."""
        column_names = [cd["id"] for cd in self.columns]
        _data = self.data.loc[:, column_names]
        return _data

    def show(self, page_size: int = 250) -> Optional[DataTable]:
        """Create table.

        Args:
            page_size (int): number of rows to display. Defaults to 250.

        Returns:
            Optional[DataTable]: DataTable containing the table
        """
        _data = self._filter_data()
        return DataTable(
            columns=self.columns,
            data=_data.to_dict("records"),
            filter_action=self.filter_action,
            sort_action=self.sort_action,
            style_table=self.style_table,
            style_data=self.style_data,
            page_size=page_size,
        )
