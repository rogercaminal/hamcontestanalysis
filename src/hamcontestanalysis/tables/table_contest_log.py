"""Dash table containing the log of the contest."""
from hamcontestanalysis.tables.table_base import TableBase


class TableContestLogCQWW(TableBase):
    """Table containing the contest log."""
    def __init__(self):
        columns = [
            {"name": "Date time", "id": "datetime", "type": "datetime"},
            {"name": "Frequency", "id": "frequency", "type": "numeric"},
            {"name": "Band", "id": "band", "type": "numeric"},
            {"name": "Mode", "id": "mode", "type": "text"},
            {"name": "Call", "id": "call", "type": "text"},
            {"name": "CQ Zone", "id": "cqz", "type": "numeric"},
            {"name": "DXCC", "id": "country", "type": "text"},
            {"name": "My Call", "id": "mycall", "type": "text"},
            # year
            # QSOS in that minute, in those 30 min, in those 60 min
            # Prefix
            # ITU zone
            # Continent
            # Copied exchange
        ]
        filter_action = 'native'
        sort_action = "native"
        style_table={'height': "300px", 'overflowY': 'auto'}
        style_data={
            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
        super().__init__(columns=columns, style_table=style_table, style_data=style_data, filter_action=filter_action, sort_action=sort_action)