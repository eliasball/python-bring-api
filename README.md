# Bring Shopping Lists API

An unofficial python package to access the Bring! shopping lists API.

> This is a **minimal** python port of the [node-bring-api](https://github.com/foxriver76/node-bring-api) by [foxriver76](https://github.com/foxriver76). All credit goes to him for making this awesome API possible!

## Disclaimer

The developers of this module are in no way endorsed by or affiliated with Bring! Labs AG, or any associated subsidiaries, logos or trademarks.

## Installation

`pip install python-bring-api`

## Documentation

See below for usage examples. See [Exceptions](#exceptions) for API-specific exceptions and mitigation strategies for common exceptions.

## Usage Example

The API is available both sync and async, where sync is the default for simplicity. Both implementations of each function use the same async HTTP library `aiohttp` in the back.

### Sync

```python
import logging
import sys

from python_bring_api.bring import Bring

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Create Bring instance with email and password
bring = Bring("MAIL", "PASSWORD")
# Login
bring.login()

# Get information about all available shopping lists
lists = bring.loadLists()["lists"]

# Save an item with specifications to a certain shopping list
bring.saveItem(lists[0]['listUuid'], 'Milk', 'low fat')

# Save another item
bring.saveItem(lists[0]['listUuid'], 'Carrots')

# Get all the items of a list
items = bring.getItems(lists[0]['listUuid'])
print(items)

# Check off an item
bring.completeItem(lists[0]['listUuid'], 'Carrots')

# Remove an item from a list
bring.removeItem(lists[0]['listUuid'], 'Milk')
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

    # Save another item
    await bring.saveItemAsync(lists[0]['listUuid'], 'Carrots')

    # Get all the items of a list
    items = await bring.getItemsAsync(lists[0]['listUuid'])
    print(items)

    # Check off an item
    await bring.completeItemAsync(lists[0]['listUuid'], 'Carrots')

    # Remove an item from a list
    await bring.removeItemAsync(lists[0]['listUuid'], 'Milk')

asyncio.run(main())
```

## Exceptions
In case something goes wrong during a request, several exceptions can be thrown.
They will either be BringRequestException, BringParseException, or BringAuthException, depending on the context. All inherit from BringException.

### Another asyncio event loop is already running

Because even the sync methods use async calls under the hood, you might encounter an error that another asyncio event loop is already running on the same thread. This is expected behavior according to the asyncio.run() [documentation](https://docs.python.org/3/library/asyncio-runner.html#asyncio.run). You cannot call the sync methods when another event loop is already running. When you are already inside an async function, you should use the async methods instead.

### Exception ignored: RuntimeError: Event loop is closed

Due to a known issue in some versions of aiohttp when using Windows, you might encounter a similar error to this:

```python
Exception ignored in: <function _ProactorBasePipeTransport.__del__ at 0x00000000>
Traceback (most recent call last):
  File "C:\...\py38\lib\asyncio\proactor_events.py", line 116, in __del__
    self.close()
  File "C:\...\py38\lib\asyncio\proactor_events.py", line 108, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "C:\...\py38\lib\asyncio\base_events.py", line 719, in call_soon
    self._check_closed()
  File "C:\...\py38\lib\asyncio\base_events.py", line 508, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
```

You can fix this according to [this](https://stackoverflow.com/questions/68123296/asyncio-throws-runtime-error-with-exception-ignored) stackoverflow answer by adding the following line of code before executing the library:
```python
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

## Changelog

### 3.0.0

Change backend library from requests to aiohttp, thanks to [@miaucl](https://github.com/miaucl)!
This makes available async versions of all methods.

Fix encoding of request data, thanks to [@miaucl](https://github.com/miaucl)!

### 2.1.0

Add notify() method to send push notifications to other list members, thanks to [@tr4nt0r](https://github.com/tr4nt0r)!

Add method to complete items, thanks to [@tr4nt0r](https://github.com/tr4nt0r)!

Fix error handling in login method, thanks to [@tr4nt0r](https://github.com/tr4nt0r)!

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
