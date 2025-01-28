from selenium import webdriver
from helpers import *
import json


driver = webdriver.Chrome()
driver.maximize_window()

competetion_index = 1
season_index = 1
cl = -1  # all clubs

url = "https://www.premierleague.com/results?co={competetion_index}&se={season_index}&cl={cl}".format(
    competetion_index=competetion_index, season_index=season_index, cl=cl
)

driver.get(url=url)
reject_all_button(driver)
all_seasons = get_all_seasons(driver=driver)

all_seasons = all_seasons[:2]

matchdays_per_season = {}

for season in all_seasons:
    season_id = season["id"]
    season_name = season["name"]

    season_url = f"https://www.premierleague.com/results?co={competetion_index}&se={season_id}&cl={cl}"

    driver.get(season_url)
    scroll(driver=driver)
    matches = extract_matches(webdriver=driver, with_tqdm=True)
    print(f"Season: {season_name}")

    matchdays_per_season[season_name] = matches

    try:
        sanitized_season_name = season_name.replace("/", "_")

        with open(file=f"data/matches_{sanitized_season_name}.json", mode="w") as f:
            json.dump(obj={"season": season_name, "matches": matches}, fp=f)
    except Exception as e:
        print(f"Failed to save matches for season {season_name}: {e}")
