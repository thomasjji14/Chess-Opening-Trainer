import subprocess
import os
import time
import sys

class Engine():
    def __init__(self):
        self.__base = subprocess.Popen(
            self.__resource_path('engine/sf.exe'),
            shell = True,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1
        )

    def evaluate_at_position(self, position, depth=18, lines=1):
        self.__base.stdin.write("ucinewgame\n")
        self.__isReady()
        self.__base.stdin.write("setoption name MultiPV value " + str(lines)+"\n")
        self.__isReady()
        self.__base.stdin.write('position fen '+position+"\n")
        self.__isReady()
        self.__base.stdin.write("go depth "+str(depth)+"\n")

        bestMoves = ["" for i in range(lines)]

        text = ""
        while not "bestmove" in text:
            text = self.__base.stdout.readline()
            if (" depth " + str(depth)) in text and "multipv" in text:
                cleanedLine = text.replace("mate ","M").replace("cp ","")
                decompLine = cleanedLine.split(" ")
                index = int(decompLine[decompLine.index("multipv")+1])-1
                
                pv_index = decompLine.index("pv")
                score_index = decompLine.index("score")
                bestMoves[index] = decompLine[pv_index + 1] + " " + decompLine[score_index + 1]
        self.__isReady()
        self.__base.stdin.write("stop\n")
        self.__isReady()
        self.__base.stdin.write("quit\n")

        return bestMoves
    
    def __isReady(self):
        self.__base.stdin.write('isready\n')
        outtext = ""
        while not "readyok" in outtext:
            outtext = self.__base.stdout.readline()

    @staticmethod
    def __resource_path(relative_path):
        """ Get absolute path for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
# sf = Engine()
# print(sf.evaluate_at_position("r1bq2nr/pppp1kpp/8/2b1n3/4P3/8/PPPP1PPP/RNBQK2R w KQ - 0 6", depth = 30, lines = 3))