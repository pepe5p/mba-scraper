from datetime import datetime, timedelta

from icalendar import Event


class GameEvent:
    MBA_DATETIME_FORMAT = "%d %b %Y, %H:%M"
    
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
        self.start_datetime = datetime.strptime(start_datetime_raw, GameEvent.MBA_DATETIME_FORMAT)

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
