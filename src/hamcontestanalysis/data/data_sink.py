"""PyContestAnalyzer Data Sink base class definition."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

DataTypeT = TypeVar("DataTypeT")


class DataSink(ABC, Generic[DataTypeT]):
    """Data Sink abstract base class.

    This abstract class serves as a base interface for the different data sinks,
    defining base data sink methods. It mainly defines the `DataSink.push` method as the
    way to push data to a sink, implemented by each data sink subclass.
    """

    # pylint: disable=too-few-public-methods

    @abstractmethod
    def push(self, data: DataTypeT) -> None:
        """Push data to data sink.

        This method is defined in each data sink implementation and takes as input some
        data to push to the data sink.
        """
