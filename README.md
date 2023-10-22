# Bring Shopping Lists API

An unofficial python package to access the Bring! shopping lists API.

> This is a **minimal** python port of the [node-bring-api](https://github.com/foxriver76/node-bring-api) by [foxriver76](https://github.com/foxriver76). All credit goes to him for making this awesome API possible!

## Disclaimer

The developers of this module are in no way endorsed by or affiliated with Bring! Labs AG, or any associated subsidiaries, logos or trademarks.

## Installation

`pip install python-bring-api`

## Usage Example

```python
from python_bring_api.bring import Bring

# Create Bring instance with email and password
bring = Bring("EMAIL", "PASSWORD")
# Login
bring.login()

# Get information about all available shopping lists
lists = bring.loadLists()

# Save an item with specifications to a certain shopping list
bring.saveItem(lists['lists'][0]['listUuid'], 'Milk', 'low fat')

# Get all the items of a list
items = bring.getItems(lists['lists'][0]['listUuid'])
print(items['purchase']) # [{'specification': 'low fat', 'name': 'Milk'}]

# Remove an item from a list
bring.removeItem(lists['lists'][0]['listUuid'], 'Milk')
```

## Changelog

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
