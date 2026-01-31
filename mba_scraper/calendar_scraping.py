from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup, SoupStrainer
from icalendar import Calendar, Event
from requests import Response


class GameEvent:
    def __init__(
        self,
        home_team_name: str,
        away_team_name: str,
        home_team_score: str | None,
        away_team_score: str | None,
        location: str,
        start_datetime_raw: str,
    ) -> None:
        self.home_team_name = home_team_name
        self.away_team_name = away_team_name
        self.home_team_score = home_team_score
        self.away_team_score = away_team_score
        self.location = location
        self.start_datetime = datetime.strptime(start_datetime_raw, "%d %b %Y, %H:%M")

    def to_ical_event(self) -> Event:
        ical_event = Event()
        ical_event.add("SUMMARY", self.summary)
        ical_event.add("LOCATION", self.location)
        ical_event.add("DTSTART", self.start_datetime)
        ical_event.add("DTEND", self.end_datetime)
        ical_event.add("DESCRIPTION", self.description)
        return ical_event

    @property
    def summary(self) -> str:
        return f"MBA: {self.home_team_name} vs {self.away_team_name}"

    @property
    def end_datetime(self) -> datetime:
        return self.start_datetime + timedelta(hours=1, minutes=30)

    @property
    def description(self) -> str:
        if self.home_team_score is None and self.away_team_score is None:
            return f"{self.home_team_name} - {self.away_team_name}"
        else:
            return f"{self.home_team_name} {self.home_team_score} - {self.away_team_score} {self.away_team_name}"


class NoGamesForTeamError(Exception):
    pass


class DOMStructureError(Exception):
    pass


def scrape_calendar(league_id: int, team_name: str) -> Calendar:
    source_url = construct_source_url(league_id=league_id)
    timeout = 15  # seconds
    response = requests.get(url=source_url, timeout=timeout)

    game_events = scrape_game_events(response=response, team_name=team_name)
    if not game_events:
        raise NoGamesForTeamError()

    return create_ical(game_events=game_events, team_name=team_name)


def construct_source_url(league_id: int) -> str:
    return f"https://hosted.dcd.shared.geniussports.com/LMBA/en/competition/{league_id}/schedule"


def scrape_game_events(response: Response, team_name: str) -> list[GameEvent]:
    strainer = SoupStrainer("div", class_="fixture-wrap")
    soup = BeautifulSoup(response.content, "lxml", parse_only=strainer)

    games = soup.select("div.match-wrap")

    events = []
    for game in games:
        try:
            home_team_name = game.select_one(
                "div.sched-teams div.home-team div.team-name a span.team-name-full",
            ).text  # type: ignore[union-attr]
            away_team_name = game.select_one(
                "div.sched-teams div.away-team div.team-name a span.team-name-full",
            ).text  # type: ignore[union-attr]
        except AttributeError as e:
            raise DOMStructureError() from e

        if team_name not in [home_team_name, away_team_name]:
            continue

        try:
            home_team_score = game.select_one(
                "div.sched-teams div.home-team div.team-score.homescore div.fake-cell"
            ).text  # type: ignore[union-attr]
        except AttributeError as e:
            raise DOMStructureError() from e

        if is_empty_string(value=home_team_score):
            home_team_score = None

        try:
            away_team_score = game.select_one(
                "div.sched-teams div.away-team div.team-score.awayscore div.fake-cell"
            ).text  # type: ignore[union-attr]
        except AttributeError as e:
            raise DOMStructureError() from e

        if is_empty_string(value=away_team_score):
            away_team_score = None

        try:
            details = game.select_one("div.match-details-wrap > div")  # type: ignore[union-attr]
            game_datetime = details.select_one("div.match-time span").text  # type: ignore[union-attr]
            venue = details.select_one("div.match-venue a").text  # type: ignore[union-attr]
        except AttributeError as e:
            raise DOMStructureError() from e

        event = GameEvent(
            home_team_name=home_team_name,
            away_team_name=away_team_name,
            home_team_score=home_team_score,
            away_team_score=away_team_score,
            location=venue,
            start_datetime_raw=game_datetime,
        )
        events.append(event)

    return events


def is_empty_string(value: str) -> bool:
    return value.isspace() or value == ""


def create_ical(game_events: list[GameEvent], team_name: str) -> Calendar:
    cal = Calendar()
    cal.add("prodid", "-//Piotr Karaś//MBA web scraper//1.0.0")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", f"MBA {team_name}")
    cal.add("X-WR-TIMEZONE", "Europe/Warsaw")
    cal.add("CALSCALE", "GREGORIAN")
    cal.add("X-PUBLISHED-TTL", "PT12H")

    for game_event in game_events:
        ical_event = game_event.to_ical_event()
        cal.add_component(component=ical_event)

    return cal
