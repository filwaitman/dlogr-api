Dlogr API documentation
=======================

__Updated:__ {{ updated_at }} UTC


Description                                                                         | Verb   | Path                                          | Auth? |
------------------------------------------------------------------------------------|--------|-----------------------------------------------|-------|
[Intro] [API Errors](#intro-api-errors)                                             |        |                                               |       |
[Intro] [Authentication](#intro-authentication)                                     |        |                                               |       |
[Intro] [`fields`/`exclude` API syntax](#intro-fieldsexclude-api-syntax)            |        |                                               |       |
[Intro] [Pagination](#intro-pagination)                                             |        |                                               |       |
--------------------------------                                                    |--------|-----------------------------------------------|-------|
[Auth] [Login](#auth-login)                                                         | POST   | /api/auth/login                               | No    |
[Auth] [Verify account](#auth-verify-account)                                       | POST   | /api/auth/verify-account                      | No    |
[Auth] [Reset password](#auth-reset-password)                                       | POST   | /api/auth/reset-password                      | No    |
[Auth] [Change password](#auth-change-password)                                     | POST   | /api/auth/change-password                     | No    |
--------------------------------                                                    |--------|-----------------------------------------------|-------|
[Customer] [List](#customer-list)                                                   | GET    | /api/customers                                | Yes   |
[Customer] [Create](#customer-create)                                               | POST   | /api/customers                                | No    |
[Customer] [Retrieve](#customer-retrieve)                                           | GET    | /api/customers/:id                            | Yes   |
[Customer] [Update](#customer-update)                                               | PATCH  | /api/customers/:id                            | Yes   |
[Customer] [Delete](#customer-delate)                                               | DELETE | /api/customers/:id                            | Yes   |
--------------------------------                                                    |--------|-----------------------------------------------|-------|
[Event] [List](#event-list)                                                         | GET    | /api/events                                   | Yes   |
[Event] [Create](#event-create)                                                     | POST   | /api/events                                   | Yes   |
[Event] [Retrieve](#event-retrieve)                                                 | GET    | /api/events/:id                               | Yes   |
[Event] [Update](#event-update)                                                     | PATCH  | /api/events/:id                               | Yes   |
[Event] [Delete](#event-delate)                                                     | DELETE | /api/events/:id                               | Yes   |





## Intro

### [Intro] API Errors

This API is designed to be REST. By doing so errors are always on `HTTP 4XX` codes (most likely `400`) and the responses for those errors will always contain human-readable messages explaining what's wrong with the request.



### [Intro] Authentication

When a login is performed successfully a property called `auth_token` will be returned on response payload. In order to make a request with this user logged in you have to send this `auth_token` value on `Authorization` header.

Example of request: `curl -X GET <API_URL>/api/events -H "Authorization: Token xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`



### [Intro] `fields`/`exclude` API syntax

All the API endpoints support `fields`/`exclude` params on querystring. `fields` syntax is handy to let API know the fields you want to be returned as response - instead of returning all of them. `exclude` does the opposite. Those params may be handy in order to get some performance boosts. Note that you can not send both params on same request (an error will be raised).

Examples of request: `curl -X GET <API_URL>/api/events?fields=id,timestamp,message` and `curl -X GET <API_URL>/api/events?exclude=id`

### [Intro] Pagination

Every "list" response has a pagination. Pagination carries the keys `count` (total of objects), `next` and `previous` (links to next and previous pages) and `results` (the returned data itself).  
Default pagination sends 30 items per page. You can navigate through items by using the pagination `limit`/`offset` technique.





## Auth

### [Auth] Login

```
POST /api/auth/login
```

Performs user login, returning the auth token (required for making authenticated requests).

__Parameters__

Name                   | Type     | Description
-----------------------|----------|---------------------------------------------
email                  | string   | `[required]` A valid email
password               | string   | `[required]` User's password

{{ auth_login }}



### [Auth] Verify account

```
POST /api/auth/verify-account
```

Verifies account and sets email as valid on API.

__Parameters__

Name                   | Type     | Description
-----------------------|----------|---------------------------------------------
token                  | string   | `[required]` User activation token (received by email)

{{ auth_verify_account }}



### [Auth] Reset password

```
POST /api/auth/reset-password
```

Triggers an email to user with password change instructions.  
Please note that this fails silently if user does not exist for privacy/security reasons.

__Parameters__

Name                   | Type     | Description
-----------------------|----------|---------------------------------------------
email                  | string   | `[required]` A valid email

{{ auth_reset_password }}



### [Auth] Change password

```
POST /api/auth/change-password
```

Changes the password of an user.  
User can be identified via either reset_token (generated on `OST /api/auth/reset-password`) or `(email/password)` pair.

__Parameters__

Name                   | Type     | Description
-----------------------|----------|---------------------------------------------
reset_token            | string   | `[required if (email/password) is not present]` User reset token (received by email)
email                  | string   | `[required if reset_token is not present]` A valid email
password               | string   | `[required if reset_token is not present]` User's current password
new_password           | string   | `[required]` User's new password

{{ auth_change_password }}





## [Customer] List

```
GET /api/customers (requires authentication)
```

Gets the customers list.  
For the time being this endpoint is disabled (you'll receive a `HTTP 405 METHOD NOT ALLOWED` on it if you try).



## [Customer] Create

```
POST /api/customers
```

Creates a new customer.  

__Parameters__

Name                   | Type     | Description
-----------------------|----------|---------------------------------------------
email                  | string   | `[required]` A valid email
password               | string   | `[required]` User's current password
name                   | string   | `[required]` User's full name
timezone               | string   | `[required]` The user timezone (such as `UTC`, `America/Sao_Paulo`, `Europe/Amsterdam` and so on)

{{ post_customers_list }}



## [Customer] Retrieve

```
GET /api/customers/:id (requires authentication)
```

Gets the customers details.  
You can only access your own customer details.

{{ get_customers_detail }}



## [Customer] Update

```
PATCH /api/customers/:id (requires authentication)
```

Updates the specified customer.  
You can only update your own customer.

__Parameters__

Name                   | Type     | Description
-----------------------|----------|---------------------------------------------
email                  | string   |  A valid email
name                   | string   |  User's full name
timezone               | string   |  The user timezone (such as `UTC`, `America/Sao_Paulo`, `Europe/Amsterdam` and so on)

{{ patch_customers_detail }}



## [Customer] Delete

```
DELETE /api/customers/:id (requires authentication)
```

DESCRIPTION

Deletes the specified customer.  
You can only delete your own customer.  
This action cannot be undone!

{{ delete_customers_detail }}





## [Event] List

```
GET /api/events (requires authentication)
```

Gets the events list.  
You will be able to see only the events related to the current authenticated customer.

{{ get_events_list }}


## [Event] Create

```
POST /api/events (requires authentication)
```

Creates a new event.  
Note that you do not send `customer` as a payload. `Event` will be linked current authenticated customer.

__Parameters__

Name                   | Type     | Description
-----------------------|----------|---------------------------------------------
object_type            | string   | `[required]` The object type (fully qualified name (including module) for the object class)
object_id              | string   | `[required]` The object id (in general terms we can say the pair (object_type/object_id) must be an universal identifier)
human_identifier       | string   | `[required]` Human-readable identifier (for display sake)
message                | string   | `[required]` Message you want to keep logged
timestamp              | ISO date | `[required]` Occurence datetime. Send this as a timezone-aware, isoformat datetime

{{ post_events_list }}



## [Event] Retrieve

```
GET /api/events/:id (requires authentication)
```

Gets the events details.  
You will be able to see only the events related to the current authenticated customer.

{{ get_events_detail }}



## [Event] Update

```
PATCH /api/events/:id (requires authentication)
```

Updates the specified customer.  
You can only update your own customer.

__Parameters__

Name                   | Type     | Description
-----------------------|----------|---------------------------------------------
object_type            | string   | The object type (fully qualified name (including module) for the object class)
object_id              | string   | The object id (in general terms we can say the pair (object_type/object_id) must be an universal identifier)
human_identifier       | string   | Human-readable identifier (for display sake)
message                | string   | Message you want to keep logged
timestamp              | ISO date | Occurence datetime. Send this as a timezone-aware, isoformat datetime

{{ patch_events_detail }}



## [Event] Delete

```
DELETE /api/events/:id (requires authentication)
```

DESCRIPTION

Deletes the specified event.  
You can only delete events from your own customer.  
This action cannot be undone!

{{ delete_events_detail }}
