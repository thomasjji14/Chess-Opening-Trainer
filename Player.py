from abc import ABC, abstractmethod
import requests
import random

class Player(ABC):

    @abstractmethod
    def getMove(self, FEN):
        pass

class lichessPlayer(Player):

    def __init__(self, variant = "standard", speeds = ["bullet", "blitz", "rapid", "classical"], ratings = [1600, 1800, 2000, 2200, 2500]):
        self.__params = {
            "variant": variant,  
            "speeds[]": speeds, 
            "ratings[]" : ratings, 
            "moves" : 999, 
            "recentGames" : 1
        }
        pass

    def getMove(self, FEN):
        self.__params['fen'] = FEN

        gameURLResponse = requests.get("https://explorer.lichess.ovh/lichess?", params = self.__params)

        json_response = gameURLResponse.json()
        moves = json_response['moves']

        moveCumFrequency = {}
        totalGames = 0
        for move in moves:
            moveCount = move['white'] + move['black'] + move["draws"]
            totalGames += moveCount
            moveCumFrequency[move['san']] = totalGames

        if totalGames == 0:
            print("Out of games.")
            raise ValueError("Done.")

        randomMoveNumber = random.randint(1, totalGames)

        return self.__getRandomMove(randomMoveNumber, moveCumFrequency)






    def __getRandomMove(self, randNum, moveFrequency):
        for key in list(moveFrequency.keys()):
            if randNum <= moveFrequency[key]:
                return key