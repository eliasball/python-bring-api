from json import JSONDecodeError
import aiohttp
import asyncio
import traceback
from typing import Dict

from .types import BringNotificationType, BringAuthResponse, BringItemsResponse, BringListResponse, BringListItemsDetailsResponse
from .exceptions import BringRequestException, BringAuthException, BringRequestException, BringParseException

import logging

_LOGGER = logging.getLogger(__name__)

class Bring:
    """
    Unofficial Bring API interface.
    """

    def __init__(self, mail: str, password: str, headers: Dict[str, str] = None, sessionAsync: aiohttp.ClientSession = None) -> None:
        self._session = sessionAsync

        self.mail = mail
        self.password = password
        self.uuid = ''
        self.publicUuid = ''

        self.url = 'https://api.getbring.com/rest/v2/'

        if headers:
            self.headers = headers
        else:
            self.headers = {
                'Authorization': '',
                'X-BRING-API-KEY': 'cof4Nc6D8saplXjE3h3HXqHH8m7VU2i1Gs0g85Sp',
                'X-BRING-CLIENT-SOURCE': 'webApp',
                'X-BRING-CLIENT': 'webApp',
                'X-BRING-COUNTRY': 'DE',
                'X-BRING-USER-UUID': ''
            }
        self.putHeaders = {
            'Authorization': '',
            'X-BRING-API-KEY': '',
            'X-BRING-CLIENT-SOURCE': '',
            'X-BRING-CLIENT': '',
            'X-BRING-COUNTRY': '',
            'X-BRING-USER-UUID': '',
            'Content-Type': ''
        }
        self.postHeaders = {
            'Authorization': '',
            'X-BRING-API-KEY': '',
            'X-BRING-CLIENT-SOURCE': '',
            'X-BRING-CLIENT': '',
            'X-BRING-COUNTRY': '',
            'X-BRING-USER-UUID': '',
            'Content-Type': ''
        }

    
    def login(self) -> BringAuthResponse:
        """
        Try to login. 
        
        Returns
        -------
        Response
            The server response object.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        BringParseException
            If the parsing of the request response fails.
        BringAuthException
            If the login fails due to missing data in the API response.
            You should check your email and password.
        """
        async def _async():
            async with aiohttp.ClientSession() as session:
                self._session = session
                res = await self.loginAsync()
                self._session = None
                return res
        return asyncio.run(_async())

    async def loginAsync(self) -> BringAuthResponse:
        """
        Try to login. 
        
        Returns
        -------
        Response
            The server response object.

        Raises
        ------
        BringRequestException
            If the request fails.
        BringParseException
            If the parsing of the request response fails.
        BringAuthException
            If the login fails due to missing data in the API response.
            You should check your email and password.
        """
        data = {
            'email': self.mail,
            'password': self.password
        }
        
        try:
            url = f'{self.url}bringauth'
            async with self._session.post(url, data=data, raise_for_status=True) as r:
                _LOGGER.debug(f"Response from %s: %s", url, r.status)
                r.raise_for_status()
                try:
                    data = await r.json()
                except JSONDecodeError as e:
                    _LOGGER.error(f'Exception: Cannot login:\n{traceback.format_exc()}')
                    raise BringParseException(f'Cannot parse login request response.') from e
        except asyncio.TimeoutError as e:
            _LOGGER.error('Exception: Cannot login:\n{traceback.format_exc()}')
            raise BringRequestException(f"Authentication failed due to connection timeout") from e
        except aiohttp.ClientError as e:
            _LOGGER.error('Exception: Cannot login:\n{traceback.format_exc()}')
            raise BringRequestException(f"Authentication failed due to request exception") from e
        
        if 'uuid' not in data or 'access_token' not in data:
            _LOGGER.error(f'Exception: Cannot login: Data missing in API response.')
            raise BringAuthException('Login failed due to missing data in the API response, please check your email and password.')
        
        self.uuid = data['uuid']
        self.publicUuid = data.get('publicUuid', '')
        self.headers['X-BRING-USER-UUID'] = self.uuid
        self.headers['Authorization'] = f'Bearer {data["access_token"]}'
        self.putHeaders = {
            **self.headers,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        self.postHeaders = {
            **self.headers,
            'Content-Type': 'application/json; charset=UTF-8'
        }
        return r

    def loadLists(self) -> BringListResponse:
        """Load all shopping lists.

        Returns
        -------
        dict

        The JSON response as a dict.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        BringParseException
            If the parsing of the request response fails.
        """
        async def _async():
            async with aiohttp.ClientSession() as session:
                self._session = session
                res = await self.loadListsAsync()
                self._session = None
                return res
        return asyncio.run(_async())

    async def loadListsAsync(self) -> BringListResponse:
        """Load all shopping lists.

        Returns
        -------
        dict

        The JSON response as a dict.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        BringParseException
            If the parsing of the request response fails.
        """
        try:
            url = f'{self.url}bringusers/{self.uuid}/lists'
            async with self._session.get(url, headers=self.headers, raise_for_status=True) as r:
                _LOGGER.debug(f"Response from %s: %s", url, r.status)
                r.raise_for_status()
                try: 
                    return await r.json()
                except JSONDecodeError as e:
                    _LOGGER.error(f'Exception: Cannot get lists:\n{traceback.format_exc()}')
                    raise BringParseException(f'Loading lists failed during parsing of request response.') from e
        except asyncio.TimeoutError as e:
            _LOGGER.error('Exception: Cannot get lists:\n{traceback.format_exc()}')
            raise BringRequestException(f"Loading list failed due to connection timeout") from e
        except aiohttp.ClientError as e:
            _LOGGER.error('Exception: Cannot get lists:\n{traceback.format_exc()}')
            raise BringRequestException(f"Loading lists failed due to request exception") from e

    def getItems(self, listUuid: str) -> BringItemsResponse:
        """
        Get all items from a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        
        Returns
        -------
        dict
            The JSON response as a dict.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        BringParseException
            If the parsing of the request response fails.
        """
        async def _async():
            async with aiohttp.ClientSession() as session:
                self._session = session
                res = await self.getItemsAsync(listUuid)
                self._session = None
                return res
        return asyncio.run(_async())

    async def getItemsAsync(self, listUuid: str) -> BringItemsResponse:
        """
        Get all items from a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        
        Returns
        -------
        dict
            The JSON response as a dict.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        BringParseException
            If the parsing of the request response fails.
        """
        try:
            url = f'{self.url}bringlists/{listUuid}'
            async with self._session.get(url, headers=self.headers, raise_for_status=True) as r:
                _LOGGER.debug(f"Response from %s: %s", url, r.status)
                r.raise_for_status()
                try:
                    return await r.json()
                except JSONDecodeError as e:
                    _LOGGER.error(f'Exception: Cannot get items for list {listUuid}:\n{traceback.format_exc()}')
                    raise BringParseException(f'Loading list items failed during parsing of request response.') from e
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot get items for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f"Loading list items failed due to connection timeout") from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot get items for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f"Loading list items failed due to request exception") from e


    def getAllItemDetails(self, listUuid: str) -> BringListItemsDetailsResponse:
        """
        Get all details from a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()

        Returns
        -------
        list
            The JSON response as a list. A list of item details.
            Caution: This is NOT a list of the items currently marked as 'to buy'. See getItems() for that.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        BringParseException
            If the parsing of the request response fails.
        """
        async def _async():
            async with aiohttp.ClientSession() as session:
                self._session = session
                res = await self.getAllItemDetailsAsync(listUuid)
                self._session = None
                return res
        return asyncio.run(_async())

    async def getAllItemDetailsAsync(self, listUuid: str) -> BringItemsResponse:
        """
        Get all details from a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()

        Returns
        -------
        list
            The JSON response as a list. A list of item details.
            Caution: This is NOT a list of the items currently marked as 'to buy'. See getItems() for that.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        BringParseException
            If the parsing of the request response fails.
        """
        try:
            url = f'{self.url}bringlists/{listUuid}/details'
            async with self._session.get(url, headers=self.headers, raise_for_status=True) as r:
                _LOGGER.debug(f"Response from %s: %s", url, r.status)
                r.raise_for_status()
                try:
                    return await r.json()
                except JSONDecodeError as e:
                    _LOGGER.error(f'Exception: Cannot get item details for list {listUuid}:\n{traceback.format_exc()}')
                    raise BringParseException(f'Loading list item details failed during parsing of request response.') from e
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot get item details for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f"Loading list item details failed due to connection timeout") from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot get item details for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f"Loading list item details failed due to request exception") from e

    def saveItem(self, listUuid: str, itemName: str, specification='') -> aiohttp.ClientResponse:
        """
        Save an item to a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        itemName : str
            The name of the item you want to save.
        specification : str, optional
            The details you want to add to the item.
        
        Returns
        -------
        Response
            The server response object.

        Raises
        ------
        BringRequestException
            If the request fails.
        """
        async def _async():
            async with aiohttp.ClientSession() as session:
                self._session = session
                res = await self.saveItemAsync(listUuid, itemName, specification)
                self._session = None
                return res
        return asyncio.run(_async())

    async def saveItemAsync(self, listUuid: str, itemName: str, specification='') -> aiohttp.ClientResponse:
        """
        Save an item to a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        itemName : str
            The name of the item you want to save.
        specification : str, optional
            The details you want to add to the item.
        
        Returns
        -------
        Response
            The server response object.

        Raises
        ------
        BringRequestException
            If the request fails.
        """
        try:
            url = f'{self.url}bringlists/{listUuid}'
            async with self._session.put(url, headers=self.putHeaders, data=f'&purchase={itemName}&recently=&specification={specification}&remove=&sender=null',  raise_for_status=True) as r:
                _LOGGER.debug(f"Response from %s: %s", url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot save item {itemName} ({specification}) to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f"Saving item {itemName} ({specification}) to list {listUuid} failed due to connection timeout") from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot save item {itemName} ({specification}) to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f"Saving item {itemName} ({specification}) to list {listUuid} failed due to request exception") from e

    
    def updateItem(self, listUuid: str, itemName: str, specification='') -> aiohttp.ClientResponse:
        """
        Update an existing list item.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        itemName : str
            The name of the item you want to update.
        specification : str, optional
            The details you want to update on the item.

        Returns
        -------
        Response
            The server response object.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        """
        async def _async():
            async with aiohttp.ClientSession() as session:
                self._session = session
                res = await self.updateItemAsync(listUuid, itemName, specification)
                self._session = None
                return res
        return asyncio.run(_async())

    async def updateItemAsync(self, listUuid: str, itemName: str, specification='') -> aiohttp.ClientResponse:
        """
        Update an existing list item.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        itemName : str
            The name of the item you want to update.
        specification : str, optional
            The details you want to update on the item.

        Returns
        -------
        Response
            The server response object.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        """
        try:
            url = f'{self.url}bringlists/{listUuid}'
            async with self._session.put(url, headers=self.putHeaders, data=f'&uuid={listUuid}&purchase={itemName}&specification={specification}', raise_for_status=True) as r:
                _LOGGER.debug(f"Response from %s: %s", url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot update item {itemName} ({specification}) to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f"Updating item {itemName} ({specification}) in list {listUuid} failed due to connection timeout") from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot update item {itemName} ({specification}) to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f"Updating item {itemName} ({specification}) in list {listUuid} failed due to request exception") from e

    
    def removeItem(self, listUuid: str, itemName: str) -> aiohttp.ClientResponse:
        """
        Remove an item from a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        itemName : str
            The name of the item you want to remove.
        
        Returns
        -------
        Response
            The server response object.

        Raises
        ------
        BringRequestException
            If the request fails.
        """
        async def _async():
            async with aiohttp.ClientSession() as session:
                self._session = session
                res = await self.removeItemAsync(listUuid, itemName)
                self._session = None
                return res
        return asyncio.run(_async())

    async def removeItemAsync(self, listUuid: str, itemName: str) -> aiohttp.ClientResponse:
        """
        Remove an item from a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        itemName : str
            The name of the item you want to remove.
        
        Returns
        -------
        Response
            The server response object.

        Raises
        ------
        BringRequestException
            If the request fails.
        """
        try:
            url = f'{self.url}bringlists/{listUuid}'
            async with self._session.put(url, headers=self.putHeaders, data=f'&purchase=&recently=&specification=&remove={itemName}&sender=null',  raise_for_status=True) as r:
                _LOGGER.debug(f"Response from %s: %s", url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot remove item {itemName} to list {listUuid}:\n{traceback.format_exc()}')
            _LOGGER.debug(_LOGGER.debug(traceback.print_exc()))
            raise BringRequestException(f"Removing item {itemName} from list {listUuid} failed due to connection timeout") from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot remove item {itemName} to list {listUuid}:\n{traceback.format_exc()}')
            _LOGGER.debug(traceback.print_exc())
            raise BringRequestException(f"Removing item {itemName} from list {listUuid} failed due to request exception") from e

    def completeItem(self, listUuid: str, itemName: str) -> aiohttp.ClientResponse:
        """
        Complete an item from a shopping list. This will add it to recent items.
        If it was not on the list, it will still be added to recent items.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        itemName : str
            The name of the item you want to complete.
        
        Returns
        -------
        Response
            The server response object.

        Raises
        ------
        BringRequestException
            If the request fails.
        """
        async def _async():
            async with aiohttp.ClientSession() as session:
                self._session = session
                res = await self.completeItemAsync(listUuid, itemName)
                self._session = None
                return res
        return asyncio.run(_async())


    async def completeItemAsync(self, listUuid: str, itemName: str) -> aiohttp.ClientResponse:
        """
        Complete an item from a shopping list. This will add it to recent items.
        If it was not on the list, it will still be added to recent items.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        itemName : str
            The name of the item you want to complete.
        
        Returns
        -------
        Response
            The server response object.

        Raises
        ------
        BringRequestException
            If the request fails.
        """
        try:
            url = f'{self.url}bringlists/{listUuid}'
            async with self._session.put(url, headers=self.putHeaders, data=f'&uuid={listUuid}&recently={itemName}',  raise_for_status=True) as r:
                _LOGGER.debug(f"Response from %s: %s", url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot complete item {itemName} to list {listUuid}:\n{traceback.format_exc()}')
            _LOGGER.debug(_LOGGER.debug(traceback.print_exc()))
            raise BringRequestException(f"Completing item {itemName} from list {listUuid} failed due to connection timeout") from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot complete item {itemName} to list {listUuid}:\n{traceback.format_exc()}')
            _LOGGER.debug(traceback.print_exc())
            raise BringRequestException(f"Completing item {itemName} from list {listUuid} failed due to request exception") from e


    def notify(self, listUuid: str, notificationType: BringNotificationType, itemName: str = None) -> aiohttp.ClientResponse:
        """
        Send a push notification to all other members of a shared list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        notificationType : BringNotificationType
        itemName : str, optional
            The text that **must** be included in the URGENT_MESSAGE BringNotificationType.

        Returns
        -------
        Response
            The server response object.

        Raises
        ------
        BringRequestException
            If the request fails.
        """
        async def _async():
            async with aiohttp.ClientSession() as session:
                self._session = session
                res = await self.notifyAsync(listUuid, notificationType, itemName)
                self._session = None
                return res
        return asyncio.run(_async())

        
    async def notifyAsync(self, listUuid: str, notificationType: BringNotificationType, itemName: str = None) -> aiohttp.ClientResponse:
        """
        Send a push notification to all other members of a shared list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()
        notificationType : BringNotificationType
        itemName : str, optional
            The text that **must** be included in the URGENT_MESSAGE BringNotificationType.

        Returns
        -------
        Response
            The server response object.

        Raises
        ------
        BringRequestException
            If the request fails.
        """
        json = {
            'arguments': [],
            'listNotificationType': notificationType.value,
            'senderPublicUserUuid': self.publicUuid
        }

        if not isinstance(notificationType, BringNotificationType):
            _LOGGER.error(f'Exception: notificationType {notificationType} not supported.')
            raise ValueError(f'notificationType {notificationType} not supported, must be of type BringNotificationType.')
        if notificationType is BringNotificationType.URGENT_MESSAGE:
            if not itemName or len(itemName) == 0 :
                _LOGGER.error('Exception: Argument itemName missing.')
                raise ValueError('notificationType is URGENT_MESSAGE but argument itemName missing.')
            else:
                json['arguments'] = [itemName]
        try:
            url = f'{self.url}bringnotifications/lists/{listUuid}'
            async with self._session.post(url, headers=self.postHeaders, json=json,  raise_for_status=True) as r:
                _LOGGER.debug(f"Response from %s: %s", url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot send notification {notificationType} for list {listUuid}:\n{traceback.format_exc()}')
            _LOGGER.debug(_LOGGER.debug(traceback.print_exc()))
            raise BringRequestException(f"Sending notification {notificationType} for list {listUuid} failed due to connection timeout") from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot send notification {notificationType} for list {listUuid}:\n{traceback.format_exc()}')
            _LOGGER.debug(traceback.print_exc())
            raise BringRequestException(f"Sending notification {notificationType} for list {listUuid} failed due to request exception") from e
