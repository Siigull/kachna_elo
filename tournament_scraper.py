import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from unidecode import unidecode

def parse_result(cell):
    """
    Parse a cell like '18w1' → (18, 'w', 1.0)
    """
    match = re.match(r"(\d+)([wb])([01½])", cell)
    if not match:
        match = re.match(r"(-\d)", cell)
        if not match:
            return None
        
        return "Pass"

    opp = int(match.group(1))
    color = match.group(2)
    res = match.group(3)
    if res == "½":
        res = 0.5
    else:
        res = float(res)
    return opp, color, res

urls = ["https://s2.chess-results.com/tnrWZ.aspx?lan=4&art=4&turdet=YES&SNode=S0&tno=732219",
        "https://s2.chess-results.com/tnrWZ.aspx?lan=5&art=4&turdet=YES&SNode=S0&tno=903949",
        "https://s3.chess-results.com/tnrWZ.aspx?lan=5&art=4&turdet=YES&SNode=S0&tno=1036014",
        "https://s1.chess-results.com/tnrWZ.aspx?lan=4&art=4&SNode=S0&tno=1129686",
        "https://s3.chess-results.com/tnrWZ.aspx?lan=1&art=4&turdet=NO&SNode=S0&tno=1159152"]

output_file = "tournament_games.txt"

with open(output_file, "a", encoding="utf-8") as f:
    f.write("white;black;white_result\n")

for url in urls:
    print(url)
    response = requests.get(url)
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", {"class": "CRs1"})

    players_data = []
    index_to_name = {}
    has_elo_col = False

    # First pass: build index mapping
    counter = 1
    for row in table.find_all("tr"):
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 6:
            continue
        # Only some tournaments have elo
        if cols[3] == "Elo":
            has_elo_col = True

        try:
            idx = int(cols[0])   # rank number
        
        except:
            idx = counter


        name = cols[2]
        index_to_name[idx] = name

        counter += 1

    # Second pass: build players data with opponent names
    for row in table.find_all("tr"):
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 6:
            continue
        
        name = cols[2]
        round_cells = []
        if has_elo_col:
            round_cells = cols[5:-4]
        else:
            round_cells = cols[4:-4]

        games = []
        for r in round_cells:
            parsed = parse_result(r)
            if parsed:
                if parsed == "Pass":
                    games.append({"Pass": True})

                else:
                    opp_idx, color, res = parsed
                    games.append({
                        "Pass": False,
                        "Opponent": index_to_name.get(opp_idx, str(opp_idx)),
                        "Color": color,
                        "Result": res
                    })
        
        pts = cols[-4]
        players_data.append({
            "Name": name,
            "Games": games,
            "Points": float(pts.replace(",", "."))
        })

    # Build DataFrame with Name as index
    df = pd.DataFrame(players_data).set_index("Name")

    with open(output_file, "a", encoding="utf-8") as f:
        # detect number of rounds from the first row
        num_rounds = len(df.iloc[0]["Games"])
        

        for r in range(num_rounds):
            players_seen = set() 
            # f.write(f"=== Round {r+1} ===\n")
            for player, row in df.iterrows():
                game = row["Games"][r]
                
                if not row["Games"][r]["Pass"]:
                    if game["Opponent"] in players_seen:
                        continue
                    f.write(f"{unidecode(player)};{ unidecode(game['Opponent'])};"
                            f"{game['Result']}\n")
                
                players_seen.add(player)
            f.write("\n")

    print(f"Games from {url} written to {output_file}")
