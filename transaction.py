from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Optional


@dataclass_json
@dataclass(frozen=True)
class TransactionStatus(object):
    ledger_state_version: int
    status: str
    confirmed_time: str


@dataclass_json
@dataclass(frozen=True)
class TransactionIdentifier(object):
    hash: str


@dataclass_json
@dataclass(frozen=True)
class Token(object):
    rri: str


@dataclass_json
@dataclass(frozen=True)
class Amount(object):
    value: str
    token_identifier: Token


@dataclass_json
@dataclass(frozen=True)
class Action(object):
    type: str
    amount: Amount
    from_account: Optional[str] = None
    from_validator: Optional[str] = None
    to_account: Optional[str] = None
    to_validator: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class Metadata(object):
    message_text: Optional[str] = None
    message: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class Transaction(object):
    transaction_status: TransactionStatus
    transaction_identifier: TransactionIdentifier
    actions: List[Action]
    fee_paid: Amount
    metadata: Metadata
