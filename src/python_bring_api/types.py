from typing import TypedDict
from typing import List


class BringList(TypedDict):
    """A list class. Represents a single list."""

    listUuid: str
    name: str
    theme: str

class BringPurchase(TypedDict):
    """A purchase class. Represents a single item."""

    name: str
    specification: str

class BringListItemDetails(TypedDict):
    """An item details class. Includes several details of an item in the context of a list.
    Caution: This does not have to be an item that is currently marked as 'to buy'."""

    uuid: str
    itemId: str
    listUuid: str
    userIconItemId: str
    userSectionId: str
    assignedTo: str
    imageUrl: str

class BringAuthResponse(TypedDict):
    """An auth response class."""

    uuid: str
    publicUuid: str
    email: str
    name: str
    photoPath: str
    bringListUUID: str
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class BringListResponse(TypedDict):
    """A list response class."""

    lists: List[BringList]

class BringItemsResponse(TypedDict):
    """An items response class."""

    uuid: str
    status: str
    purchase: List[BringPurchase]

class BringListItemsDetailsResponse(List[BringListItemDetails]):
    """A response class of a list of item details."""
    pass