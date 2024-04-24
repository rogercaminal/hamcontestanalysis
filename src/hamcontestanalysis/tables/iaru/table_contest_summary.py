"""Dash table containing the summary of the IARU HF contest."""

from pandas import DataFrame
from pandas import concat

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
            {"name": "Multipliers", "id": "is_mult", "type": "numeric"},
            {"name": "QSO points", "id": "qso_points", "type": "numeric"},
            {"name": "Contest score", "id": "score", "type": "numeric"},
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
        self.data = concat(
            [
                self.data.groupby(["year", "mycall", "band"], as_index=False).agg(
                    qsos=("is_valid", "sum"),
                    is_mult=("is_mult", "sum"),
                    qso_points=("qso_points", "sum"),
                ),
                self.data.groupby(["year", "mycall"], as_index=False)
                .agg(
                    qsos=("is_valid", "sum"),
                    is_mult=("is_mult", "sum"),
                    qso_points=("qso_points", "sum"),
                )
                .assign(score=lambda x: x["qso_points"] * x["is_mult"]),
            ]
        ).query(f"(band.isin({list(BANDMAP.keys())}) | (band.isnull()))")
        return super()._filter_data()
