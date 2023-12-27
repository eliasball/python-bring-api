import requests
import traceback
from requests.exceptions import RequestException
from .exceptions import BringError, BringAuthError, BringConnectionError

import logging

_LOGGER = logging.getLogger(__name__)

class Bring:
    """
    Unofficial Bring API interface.
    """

    def __init__(self, mail, password, headers = None):
        self.mail = mail
        self.password = password
        self.uuid = ''

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
    
    
    def login(self):
        """
        Try to login. 
        
        Returns
        -------
        Response
            The server response object."""
        data = {
            'email': self.mail,
            'password': self.password
        }
        try:
            r = requests.post(f'{self.url}bringauth', data=data)
        except RequestException as e:
            _LOGGER.error('Exception: Cannot login:')
            _LOGGER.debug(_LOGGER.debug(traceback.print_exc()))
            raise BringConnectionError(f"Authentication failed due to request exception") from e
        
        try:
            data = r.json()
        except Exception as e:
            raise BringError(f"Cannot parse login request response") from e
        
        if 'uuid' not in data or 'access_token' not in data:
            raise BringAuthError('Login failed, please check you email and password')
        
        self.uuid = data['uuid']
        self.headers['X-BRING-USER-UUID'] = self.uuid
        self.headers['Authorization'] = f'Bearer {data["access_token"]}'
        self.putHeaders = {
            'Authorization': self.headers['Authorization'],
            'X-BRING-API-KEY': self.headers['X-BRING-API-KEY'],
            'X-BRING-CLIENT-SOURCE': self.headers['X-BRING-CLIENT-SOURCE'],
            'X-BRING-CLIENT': self.headers['X-BRING-CLIENT'],
            'X-BRING-COUNTRY': self.headers['X-BRING-COUNTRY'],
            'X-BRING-USER-UUID': self.headers['X-BRING-USER-UUID'],
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        return r

    
    def loadLists(self):
        """Load all shopping lists.

        Returns
        -------
        dict
            The JSON response as a dict."""
        try:
            r = requests.get(f'{self.url}bringusers/{self.uuid}/lists', headers=self.headers)
            return r.json()
        except RequestException as e:
            _LOGGER.error('Exception: Cannot get lists: ')
            _LOGGER.debug(traceback.print_exc())
            raise BringConnectionError(f"Loading lists failed due to request exception") from e
        except Exception as e:
            _LOGGER.error('Exception: Cannot get lists: ')
            _LOGGER.debug(traceback.print_exc())
            raise BringError(f"Loading lists failed during parsing of request response") from e


    def getItems(self, listUuid):
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
        """
        try:
            r = requests.get(f'{self.url}bringlists/{listUuid}', headers = self.headers)
            return r.json()
        except RequestException as e:
            _LOGGER.error(f'Exception: Cannot get items for list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringConnectionError(f"Loading list items failed due to request exception") from e
        except Exception as e:
            _LOGGER.error(f'Exception: Cannot get items for list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringError(f"Loading list items failed during parsing of request response") from e


    def getAllItemDetails(self, listUuid):
        """
        Get all details from a shopping list.

        Parameters
        ----------
        listUuid : str
            A list uuid returned by loadLists()

        Returns
        -------
        list
            The JSON response as a list.
        """
        try:
            r = requests.get(f'{self.url}bringlists/{listUuid}/details', headers = self.headers)
            return r.json()
        except RequestException as e:
            _LOGGER.error(f'Exception: Cannot get item details for list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringConnectionError(f"Loading list item details failed due to request exception") from e
        except Exception as e:
            _LOGGER.error(f'Exception: Cannot get item details for list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringError(f"Loading list item details failed during parsing of request response") from e


    def saveItem(self, listUuid, itemName, specification=''):
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
        """
        try:
            r = requests.put(f'{self.url}bringlists/{listUuid}', headers=self.putHeaders, data=f'&purchase={itemName}&recently=&specification={specification}&remove=&sender=null')
            return r
        except RequestException as e:
            _LOGGER.error(f'Exception: Cannot save item {itemName} ({specification}) to list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringConnectionError(f"Saving item failed due to request exception") from e
        except Exception as e:
            _LOGGER.error(f'Exception: Cannot save item {itemName} ({specification}) to list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringError(f"Saving item failed during parsing of request response") from e

    
    def updateItem(self, listUuid, itemName, specification=''):
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
        """
        try:
            r = requests.put(f'{self.url}bringlists/{listUuid}', headers=self.putHeaders, data=f'&uuid={listUuid}&purchase={itemName}&specification={specification}')
            return r
        except RequestException as e:
            _LOGGER.error(f'Exception: Cannot update item {itemName} ({specification}) to list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringConnectionError(f"Updating item failed due to request exception") from e
        except Exception as e:
            _LOGGER.error(f'Exception: Cannot update item {itemName} ({specification}) to list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringError(f"Updating item failed during parsing of request response") from e

    
    def removeItem(self, listUuid, itemName):
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
        """
        try:
            r = requests.put(f'{self.url}bringlists/{listUuid}', headers=self.putHeaders, data=f'&purchase=&recently=&specification=&remove={itemName}&sender=null')
            return r
        except RequestException as e:
            _LOGGER.error(f'Exception: Cannot remove item {itemName} to list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringConnectionError(f"Removing item failed due to request exception") from e
        except Exception as e:
            _LOGGER.error(f'Exception: Cannot remove item {itemName} to list {listUuid}:')
            _LOGGER.debug(traceback.print_exc())
            raise BringError(f"Removing item failed during parsing of request response") from e
