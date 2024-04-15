# Page analyzer

### [Visit the site](https://page-analyzer-erky.onrender.com)

### Tests and linter status:
[![Actions Status](https://github.com/EvgenyCh97/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/EvgenyCh97/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/7d2ff2dc13d0ff6c0ded/maintainability)](https://codeclimate.com/github/EvgenyCh97/python-project-83/maintainability)

### Description
Web service for checking website metadata with database.

### Minimum requirements:

- python ^3.8.1

- poetry ^1.3.2

#### Database:

- PostgreSQL ^12.16

#### Modules:

- Flask ^3.0.0
- gunicorn ^20.1.0
- python-dotenv ^1.0.0
- validators ^0.22.0
- psycopg2-binary ^2.9.9
- requests ^2.31.0
- BeautifulSoup4 4.12.2

#### Linter and tests

- pytest ^7.4.2
- flake8 ^6.1.0

### Installation and launch instructions
  **Install:**
1. Clone the project
2. Install dependencies by running ```make build``` (Poetry is required)

After installing file ".env" should be created in the root directory of the project. This file must contain environment variables:
- SECRET_KEY
- DATABASE_URL (Format: {provider}://{user}:{password}@{host}:{port}/{db})

On a deployment these variables should be defined on your deploy service. 

**Dev mode with debug**

```make dev```

**Launch web-service**

```make start```
