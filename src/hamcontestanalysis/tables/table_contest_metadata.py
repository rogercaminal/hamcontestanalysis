"""Dash table containing the metadata of the contest."""

from pandas import DataFrame

from hamcontestanalysis.tables.table_base import TableBase


class TableContestMetadata(TableBase):
    """Table containing the contest log."""

    def __init__(self, callsigns_years):
        """Init method."""
        columns = [
            {"name": "Contest meta-data", "id": "metadata", "type": "text"},
        ]
        for cy in callsigns_years:
            columns.append(
                {
                    "name": f"{cy[0]} ({cy[1]})",
                    "id": f"{cy[0]} ({cy[1]})",
                    "type": "text",
                }
            )

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
        self.data = self.data.copy()
        return super()._filter_data()
