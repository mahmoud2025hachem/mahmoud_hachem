import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from helpers import match_result


datasets_json = os.listdir("data")

datas = []
for json_file in datasets_json:
    with open(f"data/{json_file}", "r") as file:
        datas.append(json.load(file))


final_output = []

for season_obj in datas:
    for match_obj in season_obj["matches"]:
        for match in match_obj["matches"]:
            obj_to_append = match
            obj_to_append["date"] = match_obj["date_long"]
            obj_to_append["season"] = season_obj["season"]
            final_output.append(obj_to_append)


df = pd.DataFrame(final_output)
df.to_csv("raw_data.csv", index=False)

df["year"] = df["date"].map(lambda x: x[-4:])
df["url"] = df["url"].map(lambda x: x[2:])
df["score"] = df["score"].map(lambda x: x.replace("\n", ""))
df["result"] = df["score"].map(match_result)
df[["home_goals", "away_goals"]] = df["score"].str.split("-", expand=True).astype(int)
df["kickoff_time"] = pd.to_datetime(df["kickoff_time"], unit="ms")

df.drop(columns=["competition", "status"], inplace=True)

print("Number of missing values:")
print(df.isnull().sum())

print("Total matches:", len(df))
print("Unique teams:", df["home_team"].nunique())
print("Seasons:", df["season"].nunique())
print("Average home goals:", df["home_goals"].mean())
print("Average away goals:", df["away_goals"].mean())


df["result"].value_counts().plot(
    kind="bar", title="Distribution des Résultats des Matchs"
)
plt.savefig("graphs/match_results_distribution.png", dpi=300, bbox_inches="tight")


df["home_points"] = df["result"].map(
    lambda x: 3 if x == "home" else (1 if x == "draw" else 0)
)
df["away_points"] = df["result"].map(
    lambda x: 3 if x == "away" else (1 if x == "draw" else 0)
)


home_points = df.groupby("home_team")["home_points"].sum()
away_points = df.groupby("away_team")["away_points"].sum()
total_points = home_points.add(away_points, fill_value=0)


home_advantage = (home_points.sum() / len(df)) - (away_points.sum() / len(df))
print("Home Advantage (Average Points per Match):", home_advantage)


plt.figure(figsize=(12, 8))
plt.bar(home_points.index, home_points, label="Points à Domicile", alpha=0.7)
plt.bar(away_points.index, away_points, label="Points à l'Extérieur", alpha=0.7)
plt.xticks(rotation=90)
plt.xlabel("Équipes")
plt.ylabel("Points")
plt.title("Points à Domicile vs. Points à l'Extérieur par Équipe")
plt.legend()
plt.savefig("graphs/points_domicile_vs_exterieur_par_equipe.png", dpi=300)


home_advantage_by_season = df.groupby("season").apply(
    lambda x: (x["home_points"].sum() / len(x)) - (x["away_points"].sum() / len(x)),
    include_groups=False,
)

plt.figure(figsize=(10, 6))
home_advantage_by_season.plot(kind="line", marker="o")
plt.xlabel("Saison")
plt.ylabel("Avantage à Domicile (Points Moyens par Match)")
plt.title("Avantage à Domicile au Fil du Temps")
plt.grid(True)
plt.savefig("graphs/avantage_domicile_au_fil_du_temps.png", dpi=300)


DATE_RANGE = f"{df["year"].min()}-{df["year"].max()}"


MINIMUM_MATCHES = 100

home_matches = df["home_team"].value_counts()
away_matches = df["away_team"].value_counts()

total_matches = home_matches.add(away_matches, fill_value=0)
filtered_teams = total_matches[total_matches >= MINIMUM_MATCHES].index
avg_home_points = home_points[filtered_teams] / home_matches[filtered_teams]
avg_away_points = away_points[filtered_teams] / away_matches[filtered_teams]
home_advantage_filtered = avg_home_points - avg_away_points
home_advantage_filtered_sorted = home_advantage_filtered.sort_values(ascending=False)

plt.figure(figsize=(12, 8))
home_advantage_filtered_sorted.plot(kind="bar", color="skyblue")
plt.xlabel("Équipes")
plt.ylabel("Avantage à Domicile (Points Moyens par Match)")
plt.title(
    f"Avantage à Domicile des Équipes de la Premier League ({DATE_RANGE}) - Min {MINIMUM_MATCHES} Matchs"
)
plt.xticks(rotation=90)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig("graphs/avantage_domicile_premier_league.png", dpi=300, bbox_inches="tight")


stadium_stats = (
    df.groupby("stadium")
    .agg(
        total_home_points=("home_points", "sum"),
        total_home_matches=("home_team", "count"),
        avg_home_points=("home_points", "mean"),
        win_rate=("result", lambda x: (x == "home").mean()),
        avg_home_goals=("home_goals", "mean"),
    )
    .reset_index()
)

away_stats = (
    df.groupby("stadium")
    .agg(
        total_away_points=("away_points", "sum"),
        total_away_matches=("away_team", "count"),
        avg_away_points=("away_points", "mean"),
        away_win_rate=("result", lambda x: (x == "away").mean()),
        avg_away_goals=("away_goals", "mean"),
    )
    .reset_index()
)

stadium_impact = pd.merge(stadium_stats, away_stats, on="stadium")
stadium_impact["home_advantage"] = (
    stadium_impact["avg_home_points"] - stadium_impact["avg_away_points"]
)
stadium_impact["goal_difference"] = (
    stadium_impact["avg_home_goals"] - stadium_impact["avg_away_goals"]
)

stadium_impact_sorted = stadium_impact.sort_values(by="home_advantage", ascending=False)

plt.figure(figsize=(16, 10))
stadium_impact_sorted.head(10).plot(
    kind="bar", x="stadium", y="home_advantage", color="skyblue"
)
plt.xlabel("Stade")
plt.ylabel("Avantage à Domicile (Points Moyens par Match)")
plt.title(f"Top 10 Stades par Avantage à Domicile ({DATE_RANGE})")
plt.xticks(rotation=90)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig("graphs/top_10_stades_par_avantage_domicile.png", dpi=300, bbox_inches="tight")


df.to_csv("cleaned_data.csv", index=False)
