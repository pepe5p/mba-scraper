from pathlib import Path
from urllib.parse import quote

from lambda_function import LEAGUE_IDS, scrape_calendar

data = [
    ("aspiration", "Singing Frogs"),
    ("recreation", "Singing Crazy Frogs"),
]

cal1 = scrape_calendar(
    league_id=LEAGUE_IDS[data[0][0]],
    team_name=data[0][1],
)

cal2 = scrape_calendar(
    league_id=LEAGUE_IDS[data[1][0]],
    team_name=data[1][1],
)

result_path = Path("singing_frogs.ics").resolve()
with open(result_path, "w") as f:
    f.writelines(cal1.to_ical().decode("utf-8"))

result_path = Path("singing_crazy_frogs.ics").resolve()
with open(result_path, "w") as f:
    f.writelines(cal2.to_ical().decode("utf-8"))

quoted_sf = quote(string=data[0][1])
quoted_scf = quote(string=data[1][1])
