from json import JSONDecodeError
import aiohttp
import asyncio
import traceback
from typing import Dict

from .types import BringNotificationType, BringAuthResponse, BringItemsResponse, BringListResponse, BringListItemsDetailsResponse, BringUserSettingsResponse
from .exceptions import BringAuthException, BringRequestException, BringParseException

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
        self.translations = {}
        self.supported_locales = ['en-AU', 'de-DE', 'fr-FR', 'it-IT','en-CA', 'nl-NL','nb-NO','pl-PL', 'pt-BR', 'ru-RU', 'sv-SE', 'de-CH', 'fr-CH', 'it-CH', 'es-ES', 'tr-TR', 'en-GB', 'en-US', 'hu-HU', 'de-AT']
        self.url = 'https://api.getbring.com/rest/v2/'
        self.url_static = 'https://web.getbring.com/'

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
            async with self._session.post(url, data=data) as r:
                _LOGGER.debug(f'Response from %s: %s', url, r.status)

                if r.status == 401:
                    try:
                        errmsg = await r.json()
                    except JSONDecodeError:
                        _LOGGER.error(f'Exception: Cannot parse login request response:\n{traceback.format_exc()}')
                    else:
                        _LOGGER.error(f'Exception: Cannot login: {errmsg["message"]}') 
                    raise BringAuthException('Login failed due to authorization failure, please check your email and password.')
                elif r.status == 400:
                    _LOGGER.error(f'Exception: Cannot login: {await r.text()}') 
                    raise BringAuthException('Login failed due to bad request, please check your email.')
                r.raise_for_status()

                try:
                    data = await r.json()
                except JSONDecodeError as e:
                    _LOGGER.error(f'Exception: Cannot login:\n{traceback.format_exc()}')
                    raise BringParseException(f'Cannot parse login request response.') from e
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot login:\n{traceback.format_exc()}')
            raise BringRequestException('Authentication failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot login:\n{traceback.format_exc()}')
            raise BringRequestException(f'Authentication failed due to request exception.') from e
        
        if 'uuid' not in data or 'access_token' not in data:
            _LOGGER.error('Exception: Cannot login: Data missing in API response.')
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
        return data

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
            async with self._session.get(url, headers=self.headers) as r:
                _LOGGER.debug(f'Response from %s: %s', url, r.status)
                r.raise_for_status()

                try: 
                    return await r.json()
                except JSONDecodeError as e:
                    _LOGGER.error(f'Exception: Cannot get lists:\n{traceback.format_exc()}')
                    raise BringParseException(f'Loading lists failed during parsing of request response.') from e
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot get lists:\n{traceback.format_exc()}')
            raise BringRequestException('Loading list failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot get lists:\n{traceback.format_exc()}')
            raise BringRequestException('Loading lists failed due to request exception.') from e

    def getItems(self, listUuid: str, locale: str = None) -> BringItemsResponse:
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
                res = await self.getItemsAsync(listUuid, locale)
                self._session = None
                return res
        return asyncio.run(_async())

    async def getItemsAsync(self, listUuid: str, locale: str = None) -> BringItemsResponse:
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
            async with self._session.get(url, headers=self.headers) as r:
                _LOGGER.debug(f'Response from %s: %s', url, r.status)
                r.raise_for_status()

                try:
                    data = await r.json()
                except JSONDecodeError as e:
                    _LOGGER.error(f'Exception: Cannot get items for list {listUuid}:\n{traceback.format_exc()}')
                    raise BringParseException('Loading list items failed during parsing of request response.') from e
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot get items for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException('Loading list items failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot get items for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException('Loading list items failed due to request exception.') from e

        if locale:
            _translations = await self.getArticleTranslationsAsync(locale)
            for item in data['purchase']:
                item['name'] = _translations.get(item['name'], item['name'])
            for item in data['recently']:
                item['name'] =_translations.get(item['name'], item['name'])
        return data

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
        Get all details of customized items from a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()

        Returns
        -------
        list
            The JSON response as a list. A list of item details.
            Caution: This is NOT a list of the items currently marked as 'to buy'. See getItems() for that.
            This contains a list of items that where customized by changing their default icon, category or uploading
            an image.
        
        Raises
        ------
        BringRequestException
            If the request fails.
        BringParseException
            If the parsing of the request response fails.
        """
        try:
            url = f'{self.url}bringlists/{listUuid}/details'
            async with self._session.get(url, headers=self.headers) as r:
                _LOGGER.debug(f'Response from %s: %s', url, r.status)
                r.raise_for_status()

                try:
                    return await r.json()
                except JSONDecodeError as e:
                    _LOGGER.error(f'Exception: Cannot get item details for list {listUuid}:\n{traceback.format_exc()}')
                    raise BringParseException(f'Loading list details failed during parsing of request response.') from e
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot get item details for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException('Loading list details failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot get item details for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException('Loading list details failed due to request exception.') from e

    def saveItem(self, listUuid: str, itemName: str, specification='', locale: str = None) -> aiohttp.ClientResponse:
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
                res = await self.saveItemAsync(listUuid, itemName, specification, locale)
                self._session = None
                return res
        return asyncio.run(_async())

    async def saveItemAsync(self, listUuid: str, itemName: str, specification='', locale: str = None) -> aiohttp.ClientResponse:
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
        if locale:
            _translations = await self.getArticleTranslationsAsync(locale, invert=True)
            itemName = _translations.get(itemName, itemName)
        data = {
            'purchase': itemName,
            'specification': specification,
        }
        try:
            url = f'{self.url}bringlists/{listUuid}'
            async with self._session.put(url, headers=self.putHeaders, data=data) as r:
                _LOGGER.debug(f'Response from %s: %s', url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot save item {itemName} ({specification}) to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Saving item {itemName} ({specification}) to list {listUuid} failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot save item {itemName} ({specification}) to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Saving item {itemName} ({specification}) to list {listUuid} failed due to request exception.') from e

    
    def updateItem(self, listUuid: str, itemName: str, specification='', locale: str = None) -> aiohttp.ClientResponse:
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
                res = await self.updateItemAsync(listUuid, itemName, specification, locale)
                self._session = None
                return res
        return asyncio.run(_async())

    async def updateItemAsync(self, listUuid: str, itemName: str, specification='', locale: str = None) -> aiohttp.ClientResponse:
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
        if locale:
            _translations = await self.getArticleTranslationsAsync(locale, invert=True)
            itemName = _translations.get(itemName, itemName)
        data = {
            'purchase': itemName,
            'specification': specification
        }
        try:
            url = f'{self.url}bringlists/{listUuid}'
            async with self._session.put(url, headers=self.putHeaders, data=data) as r:
                _LOGGER.debug(f'Response from %s: %s', url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot update item {itemName} ({specification}) to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Updating item {itemName} ({specification}) in list {listUuid} failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot update item {itemName} ({specification}) to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Updating item {itemName} ({specification}) in list {listUuid} failed due to request exception.') from e

    
    def removeItem(self, listUuid: str, itemName: str, locale: str = None) -> aiohttp.ClientResponse:
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
                res = await self.removeItemAsync(listUuid, itemName, locale)
                self._session = None
                return res
        return asyncio.run(_async())

    async def removeItemAsync(self, listUuid: str, itemName: str, locale: str = None) -> aiohttp.ClientResponse:
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
        if locale:
            _translations = await self.getArticleTranslationsAsync(locale, invert=True)
            itemName = _translations.get(itemName, itemName)
        data = {
            'remove': itemName,
        }
        try:
            url = f'{self.url}bringlists/{listUuid}'
            async with self._session.put(url, headers=self.putHeaders, data=data) as r:
                _LOGGER.debug(f'Response from %s: %s', url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot remove item {itemName} to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Removing item {itemName} from list {listUuid} failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot remove item {itemName} to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Removing item {itemName} from list {listUuid} failed due to request exception.') from e

    def completeItem(self, listUuid: str, itemName: str, locale: str = None) -> aiohttp.ClientResponse:
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
                res = await self.completeItemAsync(listUuid, itemName, locale)
                self._session = None
                return res
        return asyncio.run(_async())


    async def completeItemAsync(self, listUuid: str, itemName: str, locale: str = None) -> aiohttp.ClientResponse:
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
        if locale:
            _translations = await self.getArticleTranslationsAsync(locale, invert=True)
            itemName = _translations.get(itemName, itemName)
        data = {
            'recently': itemName
        }
        try:
            url = f'{self.url}bringlists/{listUuid}'
            async with self._session.put(url, headers=self.putHeaders, data=data) as r:
                _LOGGER.debug(f'Response from %s: %s', url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot complete item {itemName} to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Completing item {itemName} from list {listUuid} failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot complete item {itemName} to list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Completing item {itemName} from list {listUuid} failed due to request exception.') from e


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
            async with self._session.post(url, headers=self.postHeaders, json=json) as r:
                _LOGGER.debug(f'Response from %s: %s', url, r.status)
                r.raise_for_status()
                return r
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot send notification {notificationType} for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Sending notification {notificationType} for list {listUuid} failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot send notification {notificationType} for list {listUuid}:\n{traceback.format_exc()}')
            raise BringRequestException(f'Sending notification {notificationType} for list {listUuid} failed due to request exception.') from e


    def getUserSettings(self) -> BringUserSettingsResponse:
        """
        Load user settings and user list settings.

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
                res = await self.getUserSettingsAsync()
                self._session = None
                return res
        return asyncio.run(_async())

    async def getUserSettingsAsync(self) -> BringUserSettingsResponse:
        """
        Load user settings and user list settings.

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
            url = f'{self.url}bringusersettings/{self.uuid}'
            async with self._session.get(url, headers=self.headers) as r:
                _LOGGER.debug('Response from %s: %s', url, r.status)
                r.raise_for_status()
            
                try:
                    return await r.json()
                except JSONDecodeError as e:
                    _LOGGER.error(f'Exception: Cannot get user settings for uuid {self.uuid}:\n{traceback.format_exc()}')
                    raise BringParseException('Loading user settings failed during parsing of request response.') from e
        except asyncio.TimeoutError as e:
            _LOGGER.error(f'Exception: Cannot get user settings for uuid {self.uuid}:\n{traceback.format_exc()}')
            raise BringRequestException('Loading user settings failed due to connection timeout.') from e
        except aiohttp.ClientError as e:
            _LOGGER.error(f'Exception: Cannot get user settings for uuid {self.uuid}:\n{traceback.format_exc()}')
            raise BringRequestException('Loading user settings failed due to request exception.') from e


    def getArticleTranslations(self, locale: str, invert: bool = False) -> Dict:
        """
        Get articles translation table.
        
        Parameters
        ----------
        locale : str
           locale of the translation table.
        invert : str
            Return the translation table inverted.
        
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
                res = await self.getArticleTranslationsAsync(locale, invert)
                self._session = None
                return res
        return asyncio.run(_async())

    async def getArticleTranslationsAsync(self, locale: str, invert: bool = False) -> Dict:
        """
        Get articles translation table.
        
        Parameters
        ----------
        locale : str
           locale of the translation table.
        invert : str
            Return the translation table inverted.
        
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
        if locale not in self.supported_locales:
            _LOGGER.debug('Locale %s not supported by Bring.', locale)
            raise ValueError(f'Locale {locale} not supported by Bring.')

        if locale not in self.translations:

            try:
                url = f'{self.url_static}locale/articles.{locale}.json'
                async with self._session.get(url) as r:
                    _LOGGER.debug('Response from %s: %s', url, r.status)
                    r.raise_for_status()

                    try:
                        self.translations[locale] = await r.json()
                    except JSONDecodeError as e:
                        _LOGGER.error(f'Exception: Cannot load articles.{locale}.json:\n{traceback.format_exc()}')
                        raise BringParseException(f'Loading article translations for locale {locale} failed during parsing of request response.') from e
            except asyncio.TimeoutError as e:
                _LOGGER.error(f'Exception: Cannot load articles.{locale}.json::\n{traceback.format_exc()}')
                raise BringRequestException('Loading article translations for locale {locale} failed due to connection timeout.') from e
               
            except aiohttp.ClientError as e:
                _LOGGER.error(f'Exception: Cannot load articles.{locale}.json:\n{traceback.format_exc()}')
                raise BringRequestException(f'Loading article translations for locale {locale} failed due to request exception.') from e
            

        return {value:key for key, value in self.translations[locale].items()} if invert else self.translations[locale]