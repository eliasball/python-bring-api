# Bring Shopping Lists API

An unofficial python package to access the Bring! shopping lists API.

> This is a **minimal** python port of the [node-bring-api](https://github.com/foxriver76/node-bring-api) by [foxriver76](https://github.com/foxriver76). All credit goes to him for making this awesome API possible!

## Disclaimer

The developers of this module are in no way endorsed by or affiliated with Bring! Labs AG, or any associated subsidiaries, logos or trademarks.

## Installation

`pip install python-bring-api`

## Usage Example

The API is available both sync and async, where sync is the default due to simplicity and avoid breaking changes. Both implementation use the same async library `aiohttp` in the back.

### Sync

```python
import logging
import sys

from python_bring_api.bring import Bring

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

async def main():
    # Create Bring instance with email and password
    bring = Bring("MAIL", "PASSWORD")
    # Login
    bring.login()

    # Get information about all available shopping lists
    lists = bring.loadLists()["lists"]

    # Save an item with specifications to a certain shopping list
    bring.saveItem(lists[0]['listUuid'], 'Milk', 'low fat')

    # Get all the items of a list
    items = bring.getItems(lists[0]['listUuid'])
    print(items)

    # Check of an item
    bring.completeItem(lists[0]['listUuid'], items["purchase"][0]['name'])

    # Get all the recent items of a list
    items = bring.getItems(lists[0]['listUuid'])
    print(items)

    # Remove an item from a list
    bring.removeItem(lists[0]['listUuid'], 'Milk')

asyncio.run(main())
```

### Async

```python
import aiohttp
import asyncio
import logging
import sys

from python_bring_api.bring import Bring

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

async def main():
  async with aiohttp.ClientSession() as session:
    # Create Bring instance with email and password
    bring = Bring("MAIL", "PASSWORD", sessionAsync=session)
    # Login
    await bring.loginAsync()

    # Get information about all available shopping lists
    lists = (await bring.loadListsAsync())["lists"]

    # Save an item with specifications to a certain shopping list
    await bring.saveItemAsync(lists[0]['listUuid'], 'Milk', 'low fat')

    # Get all the items of a list
    items = await bring.getItemsAsync(lists[0]['listUuid'])
    print(items)

    # Check of an item
    await bring.completeItemAsync(lists[0]['listUuid'], items["purchase"][0]['name'])

    # Get all the recent items of a list
    items = await bring.getItemsAsync(lists[0]['listUuid'])
    print(items)

    # Remove an item from a list
    await bring.removeItemAsync(lists[0]['listUuid'], 'Milk')

asyncio.run(main())
```

## Exceptions
In case something goes wrong during a request, several exceptions can be thrown.
They will either be BringRequestException, BringParseException, or BringAuthException, depending on the context. All inherit from BringException.

## Changelog

### 2.0.0

Add exceptions and typings, thanks to [@miaucl](https://github.com/miaucl)!

Important: Unsuccessful HTTP status codes will now raise an exception.

Module now requires Python version >= 3.8.

### 1.2.2

Clean up unused code 🧹

### 1.2.1

Fix encoding in login request, thanks to [@tony059](https://github.com/tony059)!

### 1.2.0

Add function to update an item, thanks to [@Dielee](https://github.com/Dielee)!

### 1.1.2

Add option to provide own headers, thanks to [@Dielee](https://github.com/Dielee)!

### 1.1.0

Add item details endpoint, thanks to [@Dielee](https://github.com/Dielee)!

### 1.0.2

Fixed error handling
Added response return to login

### 1.0.1

Add github repo

### 1.0.0

Initial release
