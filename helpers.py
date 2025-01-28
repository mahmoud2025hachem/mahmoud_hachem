from tqdm import tqdm

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from selenium.webdriver.chrome.webdriver import WebDriver


def reject_all_button(driver: WebDriver):
    try:
        # Wait for the cookies modal to appear and locate the "Reject All" button
        reject_all_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div/div/button[1]")
            )
        )

        # Click the "Reject All" button
        reject_all_button.click()
        print("Cookies rejected successfully.")
    except Exception as e:
        print(f"Failed to reject cookies: {e}")


def get_all_seasons(driver: WebDriver):
    # Locate the specific season dropdown using its unique attribute
    season_dropdown = driver.find_element(
        By.CSS_SELECTOR, "div[data-dropdown-block='compSeasons']"
    )

    # Click the dropdown to expand it
    season_dropdown.click()

    # Wait for the dropdown list to be visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div[data-dropdown-block='compSeasons'] .dropdownList")
        )
    )
    # Locate all the season options within the dropdown
    season_options = season_dropdown.find_elements(
        By.CSS_SELECTOR, ".dropdownList li[role='option']"
    )

    # Extract the season names and their associated data
    seasons = []
    for option in season_options:
        season_name = option.get_attribute("data-option-name")
        season_id = option.get_attribute("data-option-id")
        seasons.append({"name": season_name, "id": season_id})

    # Print or use the extracted seasons
    return seasons


def extract_matches(webdriver: WebDriver, with_tqdm: bool = False) -> list[dict]:

    matchday_sections = webdriver.find_elements(
        by=By.CLASS_NAME, value="fixtures__date-container"
    )
    matches_list = []

    matchdays_iterator = tqdm(matchday_sections) if with_tqdm else matchday_sections

    for container in matchdays_iterator:
        # Extract the date
        date_long = container.find_element(
            by=By.CLASS_NAME, value="fixtures__date--long"
        ).text

        # Extract the competition name
        competition = container.find_element(
            by=By.CLASS_NAME, value="fixtures__competition-logo"
        ).get_attribute("alt")

        # Extract match details
        matches = container.find_elements(by=By.CLASS_NAME, value="match-fixture")
        match_details = []

        for match in matches:

            match_details.append(
                {
                    "home_team": match.get_attribute(name="data-home"),
                    "away_team": match.get_attribute(name="data-away"),
                    "competition": match.get_attribute(name="data-competition"),
                    "stadium": match.get_attribute(name="data-venue"),
                    "match_id": match.get_attribute(name="data-comp-match-item"),
                    "kickoff_time": match.get_attribute(name="data-comp-match-item-ko"),
                    "status": match.get_attribute(name="data-comp-match-item-status"),
                    "score": match.find_element(
                        By.CLASS_NAME, value="match-fixture__score"
                    ).text,
                    "url": match.find_element(
                        By.CLASS_NAME, "match-fixture__wrapper"
                    ).get_attribute("data-href"),
                }
            )

        # Append the extracted data to the list
        matches_list.append(
            {
                "date_long": date_long,
                "competition": competition,
                "matches": match_details,
            }
        )

    return matches_list


def scroll(driver: WebDriver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def match_result(score: str) -> str:
    home_goals, away_goals = score.split("-")
    home_goals = int(home_goals)
    away_goals = int(away_goals)

    if home_goals > away_goals:
        return "home"
    elif away_goals > home_goals:
        return "away"
    else:
        return "draw"