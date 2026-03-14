# Entity Relation Diagram for the Project

This document provides details for the Entity Relation diagram along with the reason behind each entity and relation

![ER Diagram](./images/E%20commerce%20ER%20diagram.png)

## Entities

### 1. Users
#### Type: Strong entity
- Used for storing user information.
- Also used to link a user to their bank account if they wish to link it.
- Each user can own __0 or more Bank accounts__, and can also place __0 or more orders__.

### 2. Bank Account
#### Type: Strong entity
- Used for storing a users banking information
- Each bank account must be linked to __1 user__, and each bank account can be used to make __0 or more order payments__.

### 3. Orders
#### Type: Strong entity
- Used for keeping track of user orders
- Each order is linked to exactly __1 user__, can be paid by exactly __1 bank account__, __can have 1 or more products__, and has exactly __1 invoice__.

### 4. Invoice
#### Type: Strong entity
- Used for maintaing invoice related to each order
- Each invoice is linked to exactly __1 order__.

### 5. Products
#### Type: Strong entity
- Used for maintaining a list of items that can be ordered
- Each product can be in __0 or more orders__, and has exactly __1 record in the inventory log__.

### 6. Inventory
#### Type: Weak entity
- Used for maintaining a track of how much inventory of the product is available.
- Each inventory log corresponds to exactly __1 product__.


## Relations

### 1. _User_ places _Orders_
#### __Cardinality__: (Users) One to Many (Orders)
#### __Type__: Total participation on the many (Orders) side.


### 2. _User_ owns _Bank account_
#### __Cardinaltiy__: (Users) One to Many (Bank Accounts)
#### __Type__: Total participation on the many (Bank Accounts) side.

### 3. _Order_ paid using _Bank account_
#### __Cardinaltiy__: (Orders) Many to One (Bank Accounts)
#### __Type__: Total participation on the many (Orders) side.

### 4. _Order_ generates _Invoice_
#### __Cardinality__: (Orders) One to One (Invoice)
#### __Type__: Total participation on both sides 

### 5. _Orders_ has list of _Products_
#### __Cardinality__: (Orders) Many to Many (Products)
#### __Type__: Total participation on the Orders side.

### 6. _Products_ has _Inventory_
#### __Cardinality__: (Products) One to One (Inventory)
#### __Type__: Identifying Relation and Total participation on both sides.