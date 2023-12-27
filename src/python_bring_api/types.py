from typing import TypedDict


class BringList(TypedDict):
    """A list class."""

    listUuid: str
    name: str
    theme: str

class BringPurchase(TypedDict):
    """A purchase class."""

    name: str
    specification: str

class BringItems(TypedDict):
    """An items class."""

    uuid: str
    status: str
    purchase: list[BringPurchase]

class BringAuthResponse(TypedDict):
    """An auth response class."""

    uuid: str
    publicUuid: str
    email: str
    name: str
    uuid: str
    photoPath: str
    bringListUUID: str
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class BringListResponse(TypedDict):
    """A list response class."""

    lists: list[BringList]
    
class BringItemsResponse(BringItems):
    """A list response class."""

    pass