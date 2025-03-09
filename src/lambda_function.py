import http
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import unquote

import requests
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from bs4 import BeautifulSoup
from icalendar.cal import Calendar, Event

warnings.filterwarnings("ignore", message=".*maxsplit.*", category=DeprecationWarning, module=r"ics\.utils")

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


LEAGUE_IDS = {
    "halloffame": 40438,
    "allstar": 40437,
    "development": 40439,
    "aspiration": 40440,
    "recreation": 40441,
}


class InvalidLeagueError(Exception):
    def __init__(self, league: str | None) -> None:
        self.league = league


class NoGamesForTeamError(Exception):
    pass


@app.exception_handler(InvalidLeagueError)
def handle_invalid_league_error(error: InvalidLeagueError) -> Response[str]:
    return Response(
        status_code=http.HTTPStatus.BAD_REQUEST,
        content_type="text/plain",
        body=f"Invalid league `{error.league}`.",
    )


@app.exception_handler(NoGamesForTeamError)
def handle_no_games_for_team_error(_: NoGamesForTeamError) -> Response[str]:
    return Response(
        status_code=http.HTTPStatus.BAD_REQUEST,
        content_type="text/plain",
        body="No games found for the given team.",
    )


@app.get("/")
def main() -> Response[str]:
    league = app.current_event.get_query_string_value(name="league")
    if not league:
        raise InvalidLeagueError(league=league)
    try:
        league_id = LEAGUE_IDS[league]
    except KeyError:
        raise InvalidLeagueError(league=league)

    team_name_quoted = app.current_event.get_query_string_value(name="team_name")
    if not team_name_quoted:
        return Response(
            status_code=http.HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
            body="Missing required query parameter `team_name`.",
        )

    team_name = unquote(string=team_name_quoted)

    try:
        calendar = scrape_calendar(league_id=league_id, team_name=team_name)
    except requests.exceptions.RequestException as e:
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


def scrape_calendar(league_id: int, team_name: str) -> Calendar:
    source_url = construct_source_url(league_id=league_id)
    page = requests.get(url=source_url)
    soup = BeautifulSoup(page.content, "html.parser")
    game_events = scrape_game_events(soup=soup, team_name=team_name)
    if not game_events:
        raise NoGamesForTeamError()
    calendar = create_ical(game_events=game_events)
    return calendar


def construct_source_url(league_id: int) -> str:
    return f"https://hosted.dcd.shared.geniussports.com/LMBA/en/competition/{league_id}/schedule"


@dataclass
class GameEventData:
    home_team: str
    away_team: str
    location: str
    start_datetime: str


def scrape_game_events(soup: BeautifulSoup, team_name: str) -> list[GameEventData]:
    games = (
        soup.body.div.find("div", class_="hs-container noresize main-container")  # type: ignore
        .div.div.find("div", class_="schedule-wrap template-wrap")
        .find("div", class_="fixture-wrap")
        .find_all("div", class_="match-wrap")
    )

    events = []
    for game in games:
        scheduled_team = game.find("div", class_="sched-teams")
        home_team = (
            scheduled_team.find("div", class_="home-team")
            .find("div", class_="team-name")
            .a.find("span", class_="team-name-full")
            .text
        )
        away_team = (
            scheduled_team.find("div", class_="away-team")
            .find("div", class_="team-name")
            .a.find("span", class_="team-name-full")
            .text
        )
        if team_name not in [home_team, away_team]:
            continue

        details = game.find("div", class_="match-details-wrap").div
        game_datetime = details.find("div", class_="match-time").span.text
        venue = details.find("div", class_="match-venue").a.text
        event = GameEventData(
            home_team=home_team,
            away_team=away_team,
            location=venue,
            start_datetime=game_datetime,
        )
        events.append(event)

    return events


def create_ical(game_events: list[GameEventData]) -> Calendar:
    cal = Calendar()
    cal.add("prodid", "-//MBA league calednar//mxm.dk//")
    cal.add("version", "2.0")

    for game_event in game_events:
        ical_event = Event()
        ical_event.add("SUMMARY", f"MBA: {game_event.home_team} vs {game_event.away_team}")
        ical_event.add("LOCATION", game_event.location)
        utc_datetime = datetime.strptime(game_event.start_datetime, "%d %b %Y, %H:%M")
        ical_event.add("DTSTART", utc_datetime)
        ical_event.add("DTEND", utc_datetime + timedelta(hours=1, minutes=30))
        cal.add_component(ical_event)

    return cal
