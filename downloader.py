import requests
import json
import time
import copy
import pickle


ECO_INDEX = 7
OPENING_INDEX = 1
GAME_MOVES = 0
GAME_OUTCOME = 1



# startTime = time.time()
# Start from the beginning, then keep going
# Idea: Change the start date (+1 month) once it's verified that all
#       data within a month is done.
# Keep an archieve of already seen games
START_MONTH = "02"
START_YEAR = "2021"

def downloadGames(username):
    # Gets user game data
    gameURLResponse = requests.get('https://api.chess.com/pub/player/' + username + '/games/archives')

    # Retrieves past monthy game archieves, oldest -> newest
    gameURLs = gameURLResponse.json()['archives']

    #Gets the monthly games, and adds them to a large list of games
    games = []
    for url in gameURLs:
        month = url.split("/")[-1]
        year = url.split("/")[-2]
        if int(year) > int(START_YEAR) or ((int(year) == int(START_YEAR)) and int(month) >= int(START_MONTH)):
            monthlyGamesResponse = requests.get(url)
            monthlyGames = monthlyGamesResponse.json()['games']
            games += monthlyGames

    return games


games = downloadGames("bankericebutt")






# print(type(games))
# print(games[0])
# with open("bankerice.pkl", "wb") as f:
#     pickle.dump(games, f)
# with open("dump.txt", "w") as f:
#     json.dump(games, f)




# The opening repotoire needs to be sorted, one as black, one as white
# as to distinguish my moves from my opponents moves.
# Should also go from most recent to oldest, going to the first game