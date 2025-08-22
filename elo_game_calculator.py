import pandas as pd
import json

df = pd.read_csv("tournament_games.txt", delimiter=";", encoding="utf-8")

players = {}

for index, value in df.iterrows():
    if value["white"] not in players:
        players[value["white"]] = {"elo": 1000, "game_hist": []}
    if value["black"] not in players:
        players[value["black"]] = {"elo": 1000, "game_hist": []}

for index, [white, black, result] in df.iterrows():
    res = float(result)
    dif = 1 / (1 + 10**((players[white]["elo"] - players[black]["elo"]) / 400))
    elo_calc = 40 * (res - dif)
    players[white]["elo"] += elo_calc
    players[white]["game_hist"].append([black, players[white]["elo"], "white"])
    players[black]["elo"] -= elo_calc
    players[black]["game_hist"].append([white, players[black]["elo"], "black"])

sorted_players = sorted(players.items(), key=lambda x: x[1]["elo"], reverse=True)

with open("data.json", "w") as json_file:
    json.dump(sorted_players, json_file)
