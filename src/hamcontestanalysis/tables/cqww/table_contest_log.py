"""Dash table containing the log of the contest."""

from pandas import DataFrame

from hamcontestanalysis.tables.table_base import TableBase


class TableContestLog(TableBase):
    """Table containing the contest log."""

    def __init__(self):
        """Init method."""
        columns = [
            {"name": "Date time", "id": "datetime", "type": "datetime"},
            {"name": "Frequency", "id": "frequency", "type": "numeric"},
            {"name": "Band", "id": "band", "type": "numeric"},
            {"name": "Mode", "id": "mode", "type": "text"},
            {"name": "Call", "id": "call", "type": "text"},
            {"name": "CQ Zone", "id": "zone", "type": "numeric"},
            {"name": "DXCC", "id": "country", "type": "text"},
            {"name": "My Call", "id": "mycall", "type": "text"},
            {"name": "Year", "id": "year", "type": "numeric"},
            {"name": "Mult. zone", "id": "is_zone", "type": "numeric"},
            {"name": "Mult. DXCC", "id": "is_dxcc", "type": "numeric"},
            # {"name": "QSOs last 10 min", "id": "rate_10", "type": "numeric"},
            # {"name": "QSOs last 30 min", "id": "rate_30", "type": "numeric"},
            # {"name": "QSOs last 60 min", "id": "rate_60", "type": "numeric"},
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
            self.data.copy()
            # .join(
            #     self.data.set_index("datetime")
            #     .groupby(["mycall", "year"])[["is_valid"]]
            #     .transform(lambda d: d.rolling("10T", min_periods=1).sum())
            #     .reset_index(drop=True)
            #     .rename(columns={"is_valid": "rate_10"})
            # )
            # .join(
            #     self.data.set_index("datetime")
            #     .groupby(["mycall", "year"])[["is_valid"]]
            #     .transform(lambda d: d.rolling("30T", min_periods=1).sum())
            #     .reset_index(drop=True)
            #     .rename(columns={"is_valid": "rate_30"})
            # )
            # .join(
            #     self.data.set_index("datetime")
            #     .groupby(["mycall", "year"])[["is_valid"]]
            #     .transform(lambda d: d.rolling("60T", min_periods=1).sum())
            #     .reset_index(drop=True)
            #     .rename(columns={"is_valid": "rate_60"})
            # )
        )
        return super()._filter_data()
