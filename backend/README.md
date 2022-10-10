<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->

<a name="readme-top"></a>

<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- TABLE OF CONTENTS -->

#### Table of Contents

<ol>
<li>
    <a href="#watchb-backend">WatchB Backend</a>
    <ul>
    <li><a href="#built-with">Built With</a></li>
    </ul>
</li>
<li>
    <a href="#getting-started">Getting Started</a>
    <ul>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#installation">Installation</a></li>
    </ul>
</li>
<li>
    <a href="#usage">Usage</a>
    <ul>
    <li><a href="#migrate-local-database">Migrate local database</a></li>
    <li><a href="#run-local-server">Run local server</a></li>
    <li><a href="#crawl-and-register-movies">Crawl and register movies</a></li>
    </ul>
</li>
<li><a href="#roadmap">Roadmap</a></li>
</ol>

<!-- ABOUT THE PROJECT -->

## WatchB Backend

WatchB backend server provides...

- database models for storing data repeatedly reused in-service
- RESTful API endpoints to access to those models data
- user authentication w/ JWT
- movies crawling interface to fetch numerous movies data from web and populate the service resource to serve

### Built With

- [![Django][django]][django-url]
- [![Django REST framework][drf]][drf-url]

<!-- GETTING STARTED -->

## Getting Started

### Prerequisites

- Python 3.10
- [Poetry 1.1](https://python-poetry.org/docs/1.1/)
  - Linux, macOS, Windows (WSL)
    ```sh
    $ curl -sSL https://install.python-poetry.org | python3 -
    ```
  - Windows (Powershell)
    ```sh
    $ (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
    ```
- .env file

  If you have cross origin servers accessing to WatchB backend API endpoints, specify them as a **comma separated** environment variable in `backend/.env` file

  ```
  CORS_ALLOWED_ORIGINS=<YOUR_ALLOWED_ORIGIN1>,<YOUR_ALLOWED_ORIGIN2>,...
  ```

- VS Code (Recommended)

  If you choose VS Code as an editor, you can utilize provided [settings](.vscode/settings.json) in this repo.

### Installation

1. Clone the repo
   ```sh
   $ git clone https://github.com/mynghn/watchb.git
   ```
2. Go to `backend` directory & Install dependencies w/ poetry
   ```sh
   $ cd backend
   $ poetry install --no-root
   ```
   _You can check out the exact dependency versions specified in [pyproject.toml](pyproject.toml) file_

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

There are more admin commands provided, other than ones introduced below. _For more admin command information, please refer to the [Django documentation](https://docs.djangoproject.com/en/4.0/ref/django-admin/)_

**\*All commands described here assumes you are at `backend` directory**

### Migrate local database

If you want to run server w/ local database, you should prepare your own by applying migration files provided in this repository. (`accounts/migrations`, `movies/migrations`)

1. Prepare local database file in the _backend_ directory
2. Migrate
   ```sh
   $ python3 manage.py migrate
   ```

### Run local server

Use command below for running local dev server for debugging purpose or else.

(_If you are planning interactions between frontend server, make sure to configure allowed origins in `backend/.env` file as described [above](#prerequisites)_, before running backend server)

```sh
$ python3 manage.py runserver
```

### Crawl and register movies

You can fetch movies data from open API and register it to your database for future serving.

WatchB provides interface to send requests to [TMDB](https://developers.themoviedb.org/3) & [KMDb](https://www.kmdb.or.kr/info/api/apiDetail/6) open APIs. Get your own API authentication keys and use command below to populate your movies database.

1. Prepare your own API keys.

   You can set them as environment variables or pass them to the command later with `--tmdb-token` and `--kmdb-key` options.

   ```sh
   $ export TMDB_API_TOKEN=$YOUR_TMDB_API_JWT
   $ export KMDB_API_KEY=$YOUR_KMDB_API_KEY
   ```

2. Choose options and crawl movies.

   Below is one example of many possible options. _For more information, check out `-h` or `--help` option_

   ```sh
   $ python3 manage.py crawlmovies --list-method TopRated --detail-method Complementary --max-count 1000 --debug
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [x] user authentication
  - [x] user model design
  - [x] user viewset
  - [x] JWT authentication
- [x] movies crawling &rarr; deserialize & register
  - [x] API agents
  - [x] movie domain models design
  - [x] validate & deserialize API response to django model instances
  - [x] django admin command interface
- [x] user follow
  - [x] model design
  - [x] API endpoints w/ viewsets
- [x] user update API
- [x] user &lrarr; movie interactions
  - [x] models design
  - [x] API endpoints w/ viewsets
- [ ] search
- [ ] recommendation

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[django]: https://img.shields.io/badge/Django-44B78B?style=flat-squre&logo=django&logoColor=092E20
[django-url]: https://www.djangoproject.com/
[drf]: https://img.shields.io/badge/Django%20REST%20framework-2C2C2C?style=flat-square&logo=django&logoColor=A30000
[drf-url]: https://www.django-rest-framework.org/
