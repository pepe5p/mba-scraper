# mba-scraper

AWS Lambda code that scrapes schedule from MBA League website and returns .ics calendar with games.

1. Build docker image:
    ```
    docker compose build mba-scraper
    ```

2. Run docker container:
    ```
    docker compose mba-scraper run bash
    ```
    or with make
    ```
    make dc_bash
    ```

3. Run tests:
    ```
    make test
    ```
