"""Dash table containing the summary of the contest."""
from pandas import DataFrame, concat

from hamcontestanalysis.tables.table_base import TableBase
from hamcontestanalysis.utils import BANDMAP


class TableContestSummary(TableBase):
    """Table containing the contest summary."""

    def __init__(self):
        """Init method."""
        columns = [
            {"name": "Year", "id": "year", "type": "numeric"},
            {"name": "My Call", "id": "mycall", "type": "text"},
            {"name": "Band", "id": "band", "type": "numeric"},
            {"name": "QSOs", "id": "qsos", "type": "numeric"},
            {"name": "CQ Zone", "id": "zones", "type": "numeric"},
            {"name": "DXCC", "id": "dxcc", "type": "numeric"},
        ]
        filter_action = "native"
        sort_action = "native"
        style_table = {"height": "300px", "overflowY": "auto"}
        style_data = {
            "width": "150px",
            "minWidth": "150px",
            "maxWidth": "150px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        }
        super().__init__(
            columns=columns,
            style_table=style_table,
            style_data=style_data,
            filter_action=filter_action,
            sort_action=sort_action,
        )

    def _filter_data(self) -> DataFrame:
        self.data = (
            concat(
                [
                    self.data
                    .groupby(["year", "mycall", "band"], as_index=False)
                    .agg(
                        qsos=("is_valid", "sum"), 
                        zones=("is_zone", "sum"), 
                        dxcc=("is_dxcc", "sum")
                    ), 
                    self.data
                    .groupby(["year", "mycall"], as_index=False)
                    .agg(
                        qsos=("is_valid", "sum"), 
                        zones=("is_zone", "sum"), 
                        dxcc=("is_dxcc", "sum")
                    )
                ]
            )
            .query(f"band.isin({list(BANDMAP.keys())})")
        )
        return super()._filter_data()
