import pandas as pd
import json

df = pd.read_csv("tournament_games.txt", delimiter=";", encoding="utf-8")

players = {}

for index, value in df.iterrows():
    if value["white"] not in players:
        players[value["white"]] = {"elo": 1000, "game_hist": []}
    if value["black"] not in players:
        players[value["black"]] = {"elo": 1000, "game_hist": []}

for index, [white, black, result, game_url] in df.iterrows():
    K = 40

    score_white = float(result)
    score_black = 1 - score_white
    
    expected_white = 1 / (1 + 10**((players[black]["elo"] - players[white]["elo"]) / 400))
    expected_black = 1 - expected_white

    players[white]["elo"] += K * (score_white - expected_white)
    players[black]["elo"] += K * (score_black - expected_black)

    players[white]["game_hist"].append([black, players[white]["elo"], "white", game_url])
    players[black]["game_hist"].append([white, players[black]["elo"], "black", game_url])

sorted_players = sorted(players.items(), key=lambda x: x[1]["elo"], reverse=True)

with open("data.json", "w") as json_file:
    json.dump(sorted_players, json_file)
