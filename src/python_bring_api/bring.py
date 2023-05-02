import requests
import traceback

class Bring:
    """
    Unofficial Bring API interface.
    """

    def __init__(self, mail, password):
        self.mail = mail
        self.password = password
        self.url = 'https://api.getbring.com/rest/v2/'
        self.uuid = ''
        self.name = ''
        self.bearerToken = ''
        self.refreshToken = ''
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
        try:
            r = requests.post(f'{self.url}bringauth', data=f'email={self.mail}&password={self.password}')
        except:
            print('Exception: Cannot login:')
            traceback.print_exc()
            raise
        
        data = r.json()
        self.name = data['name']
        self.uuid = data['uuid']
        self.bearerToken = data['access_token']
        self.refreshToken = data['refresh_token']

        self.headers['X-BRING-USER-UUID'] = self.uuid
        self.headers['Authorization'] = f'Bearer {self.bearerToken}'
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
        except:
            print('Exception: Cannot get lists: ')
            traceback.print_exc()
            raise


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
            r = requests.get(f'{self.url}bringlists/{listUuid}', headers = self.headers);
            return r.json();
        except:
            print(f'Exception: Cannot get items for list {listUuid}:')
            traceback.print_exc()
            raise


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
            r = requests.get(f'{self.url}bringlists/{listUuid}/details', headers = self.headers);
            return r.json();
        except:
            print(f'Exception: Cannot get item details for list {listUuid}:')
            traceback.print_exc()
            raise


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
        except:
            print(f'Exception: Cannot save item {itemName} ({specification}) to {listUuid}:')
            traceback.print_exc()
            raise

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
        except:
            print(f'Exception: Cannot remove item {itemName} from {listUuid}:')
            traceback.print_exc()
            raise