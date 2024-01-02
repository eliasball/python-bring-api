# Bring Shopping Lists API

An unofficial python package to access the Bring! shopping lists API.

> This is a **minimal** python port of the [node-bring-api](https://github.com/foxriver76/node-bring-api) by [foxriver76](https://github.com/foxriver76). All credit goes to him for making this awesome API possible!

## Disclaimer

The developers of this module are in no way endorsed by or affiliated with Bring! Labs AG, or any associated subsidiaries, logos or trademarks.

## Installation

`pip install python-bring-api`

## Usage Example

```python
import logging
import sys
from python_bring_api.bring import Bring

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Create Bring instance with email and password
bring = Bring("EMAIL", "PASSWORD")
# Login
bring.login()

# Get information about all available shopping lists
lists = bring.loadLists()["lists"]

# Save an item with specifications to a certain shopping list
bring.saveItem(lists[0]['listUuid'], 'Milk', 'low fat')

# Get all the items of a list
items = bring.getItems(lists[0]['listUuid'])
print(items['purchase']) # [{'specification': 'low fat', 'name': 'Milk'}]

# Remove an item from a list
bring.removeItem(lists[0]['listUuid'], 'Milk')
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
