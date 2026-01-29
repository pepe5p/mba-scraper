import http
from typing import Any
from urllib.parse import unquote

import requests
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from loguru import logger

from calendar_scraping import DOMStructureError, NoGamesForTeamError, scrape_calendar

app = APIGatewayHttpResolver()


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    """
    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    return app.resolve(event, context)


class InvalidLeagueIDError(Exception):
    def __init__(self, league_id: int | str | None) -> None:
        self.league_id = league_id


@app.exception_handler(InvalidLeagueIDError)
def handle_invalid_league_error(error: InvalidLeagueIDError) -> Response[str]:
    logger.error(f"Invalid league `{error.league_id}`.")
    return Response(
        status_code=http.HTTPStatus.BAD_REQUEST,
        content_type="text/plain",
        body=f"Invalid league `{error.league_id}`.",
    )


@app.exception_handler(NoGamesForTeamError)
def handle_no_games_for_team_error(_: NoGamesForTeamError) -> Response[str]:
    logger.error("No games found for the given team.")
    return Response(
        status_code=http.HTTPStatus.BAD_REQUEST,
        content_type="text/plain",
        body="No games found for the given team.",
    )


@app.exception_handler(DOMStructureError)
def handle_dom_structure_error(_: DOMStructureError) -> Response[str]:
    logger.error("DOM structure error.")
    return Response(
        status_code=http.HTTPStatus.BAD_REQUEST,
        content_type="text/plain",
        body="Cannot parse MBA website.",
    )


@app.get("/")
def main() -> Response[str]:
    league_id_raw = app.current_event.get_query_string_value(name="league_id")
    if not league_id_raw:
        raise InvalidLeagueIDError(league_id=league_id_raw)

    team_name_quoted = app.current_event.get_query_string_value(name="team_name")
    if not team_name_quoted:
        logger.error("Missing required query parameter `team_name`.")
        return Response(
            status_code=http.HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
            body="Missing required query parameter `team_name`.",
        )

    league_id = int(league_id_raw)
    team_name = unquote(string=team_name_quoted)

    try:
        calendar = scrape_calendar(league_id=league_id, team_name=team_name)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch MBA website: {e}")
        return Response(
            status_code=http.HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
            body=f"Failed to fetch MBA website: {e}",
        )

    return Response(
        status_code=http.HTTPStatus.OK,
        content_type="text/plain; charset=utf-8",
        body=calendar.to_ical().decode("utf-8"),
    )
