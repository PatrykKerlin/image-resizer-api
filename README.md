# Image RESTful API

## API for HexOcean recruitment process.

API for storing images and generating thumbnails.

##

Django: 4.1.7  
Django REST Framework: 3.14  
PostgreSQL: 15.2

##

This app was created using Docker containers.
To run it type "docker-compose up" in the command line.

##

During the first boot, there will be created an admin account and 3 tiers (Basic, Premium, Enterprise).  
Global caching is set to 15 seconds in settings file.

##

### Authorization required!

You can choose:

-   JWT Tokens stored in httponly cookies
-   Token-based authentication with required prefix "Token"  
    Name: Authorization  
    In: header

##

### Available endpoints:

**Full documentation:** api/docs/

##

-   **POST -> api/user/jwt-login/**

    -   Request body:
        -   username (string)
        -   password (string)
    -   Response:
        -   Status code: 200
        -   Response body: {"success": bool}

-   **POST -> api/user/jwt-logout/**
    -   Response:
        -   Status code: 204

##

-   **POST -> api/user/token/**
    -   Request body:
        -   username (string)
        -   password (string)
    -   Response:
        -   Status code: 200
        -   Response body: {"token": "string"}

##

-   **GET -> api/user/images/**
    -   Response:
        -   Status code: 200
        -   Response body: [{"id": 0, "image": "string"}]
-   **POST -> api/user/images/**
    -   Request body: image (string ($binary))
    -   Response:
        -   Status code: 201
        -   Response body: {"id": 0, "image": "string"}
-   **GET -> api/user/images/{id}/**
    -   Parameters: - id (integer (path))
    -   Response:
        -   Status code: 200
        -   Response body: {"id": 0, "image": "string"}
-   **DELETE -> api/user/images/{id}/**
    -   Parameters:
        -   id (integer (path))
    -   Response:
        -   Status code: 204

##

-   **GET -> api/user/thumbnails/**
    -   Response:
        -   Status code: 200
        -   Response body: [{"id": 0, "image_id": 0, "height": 0, "thumbnail": "string"}]
-   **GET -> api/user/thumbnails/{id}/**
    -   Parameters: - id (integer (path))
    -   Response:
        -   Status code: 200
        -   Response body: {"id": 0, "image_id": 0, "height": 0, "thumbnail": "string"}
-   **DELETE -> api/user/thumbnails/{id}/**
    -   Parameters:
        -   id (integer (path))
    -   Response:
        -   Status code: 204

##

-   **GET -> api/user/link/{id}/**
    -   Parameters: - id (integer (path)) - time (integer (query))
    -   Response:
        -   Status code: 200
        -   Response body: {"url": "string", "expires_in": 0}

##

-   **GET -> api/schema/**
    -   Parameters: - id (string (query)) - lang (string (query))
    -   Response:
        -   Status code: 200
