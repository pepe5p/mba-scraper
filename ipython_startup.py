from pathlib import Path

from mba_scraper.calendar_scraping import scrape_calendar

data = [
    ("all_star", 48242, "Singing Frogs"),
    ("recreation", 48246, "Singing Crazy Frogs"),
]

cal1 = scrape_calendar(
    league_id=data[0][1],
    team_name=data[0][2],
)

cal2 = scrape_calendar(
    league_id=data[1][1],
    team_name=data[1][2],
)

result_path = Path("singing_frogs.ics").resolve()
with open(result_path, "w") as f:
    f.writelines(cal1.to_ical().decode("utf-8"))

result_path = Path("singing_crazy_frogs.ics").resolve()
with open(result_path, "w") as f:
    f.writelines(cal2.to_ical().decode("utf-8"))
