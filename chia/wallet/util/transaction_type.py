from __future__ import annotations

from enum import IntEnum


class TransactionType(IntEnum):
    INCOMING_TX = 0
    OUTGOING_TX = 1
    COINBASE_REWARD = 2
    FEE_REWARD = 3
    INCOMING_TRADE = 4
    OUTGOING_TRADE = 5
    INCOMING_CLAWBACK = 6
    OUTGOING_CLAWBACK = 7
    OUTGOING_CLAIM = 8
