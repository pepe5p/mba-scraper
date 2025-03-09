from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

url = "https://hosted.dcd.shared.geniussports.com/LMBA/en/competition/40441/schedule?"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
games = (
    soup
    .body
    .div
    .find("div", class_="hs-container noresize main-container")
    .div
    .div
    .find("div", class_="schedule-wrap template-wrap")
    .find("div", class_="fixture-wrap")
    .find_all("div", class_="match-wrap")
)


@dataclass
class GameEventData:
    home_team: str
    away_team: str
    location: str
    start_datetime: str


TEAM_NAME = "Singing Crazy Frogs"

events = []
for game in games:
    scheduled_team = game.find("div", class_="sched-teams")
    home_team = scheduled_team.find("div", class_="home-team").find("div", class_="team-name").a.find("span",
                                                                                                      class_="team-name-full").text
    away_team = scheduled_team.find("div", class_="away-team").find("div", class_="team-name").a.find("span",
                                                                                                      class_="team-name-full").text
    
    if TEAM_NAME not in [home_team, away_team]:
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


def create_ical(game_events: list[GameEventData]) -> Calendar:
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    
    for game_event in game_events:
        ical_event = Event()
        ical_event.add("SUMMARY", f"MBA: {game_event.home_team} vs {game_event.away_team}")
        ical_event.add("LOCATION", game_event.location)
        utc_datetime = datetime.strptime(game_event.start_datetime, "%d %b %Y, %H:%M")
        ical_event.add("DTSTART", utc_datetime)
        ical_event.add("DTEND", utc_datetime + timedelta(hours=2))
        cal.add_component(ical_event)
    
    return cal


cal = create_ical(game_events=events)

result_path = Path("result.ics").resolve()
with open(result_path, "w") as f:
    f.writelines(cal.to_ical().decode("utf-8"))
