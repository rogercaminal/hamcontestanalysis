"""Data Source base class definition."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

DataTypeT = TypeVar("DataTypeT")


class DataSource(ABC, Generic[DataTypeT]):
    """Data Source abstract base class.

    This abstract class serves as a base interface for the different data sources,
    defining base data source methods. It mainly defines the `DataSource.load`
    method as the way to access the data, implemented by each data source subclass.
    """

    # pylint: disable=too-few-public-methods

    @abstractmethod
    def load(self) -> DataTypeT:
        """Load data from data source.

        This method is defined in each data source implementation and returns the
        source's data.
        """
