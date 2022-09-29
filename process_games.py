#!/bin/python3

import chess
import chess.pgn
import time, os, json
import multiprocessing

from subprocess import Popen, PIPE

THREADS = multiprocessing.cpu_count()
PLAYERS = ['Carlsen', 'Engines', 'Firouzja', 'Giri', 'Liren', 'Nakamura', 'Nepomniachtchi', 'Niemann', 'So']
ENGINE  = 'Engines/Stockfish-15'

class Engine():

    def __init__(self, ename):
        self.engine = Popen([ename], stdin=PIPE, stdout=PIPE, universal_newlines=True, shell=True)
        self.uci_ready()

    def write_line(self, line):
        self.engine.stdin.write(line)
        self.engine.stdin.flush()

    def read_line(self):
        return self.engine.stdout.readline().rstrip()

    def uci_ready(self):
        self.write_line('isready\n')
        while self.read_line() != 'readyok': pass

    def uci_search(self, fen, depth):
        self.uci_ready()
        self.write_line('position fen %s\ngo depth %d\n' % (fen, depth))
        return list(self.uci_bestmove())

    def uci_bestmove(self):
        while True:
            line = self.read_line()
            if line.startswith('bestmove'): break
            yield line

    def uci_quit(self):
        self.write_line('quit\n')

def process_pgns(player, filenames, engine_name):
    for filename in filenames:
        process_pgn(player, filename, engine_name)

def process_pgn(player, filename, engine_name):

    start_time = time.time()

    engine = Engine(engine_name)

    engine.uci_ready()
    engine.write_line('setoption name MultiPV value 3\n')
    engine.uci_ready()

    with open('%s/%s' % (player, filename)) as fin:
        game = chess.pgn.read_game(fin)

    data = {
        'positions' : [],
        'played'    : [],
        'analysis'  : [],
        'pgn'       : str(game)
    }

    for fen, move in extract_positions_for_player(player, game):

        output = engine.uci_search(fen, depth=18)
        table = parse_multipv_table(output, depths=[14, 16, 18])

        data['played'].append(move)
        data['positions'].append(fen)
        data['analysis'].append(table)

    engine.uci_quit()

    with open('%s-%s.analysis' % (player, filename), 'w') as fout:
        json.dump(data, fout)

    print ('Finished analysis for %s/%s in %.2f seconds' % (player, filename, time.time() - start_time))

def extract_positions_for_player(player, game):

    positions = []

    board = game.board()
    for move in game.mainline_moves():
        positions.append((board.fen(), str(move)))
        board.push(move)

    is_white = player in game.headers['White']
    is_black = player in game.headers['Black']
    assert is_white != is_black

    if is_white:
        return [(fen, move) for fen, move in positions if ' w ' in fen]

    if is_black:
        return [(fen, move) for fen, move in positions if ' b ' in fen]

def parse_multipv_table(output, depths):

    table = { depth : [] for depth in depths }

    for line in output:

        if any([f in line for f in ['lowerbound', 'upperbound', 'currmove']]):
            continue

        if not any([' depth %d ' % (depth) in line for depth in depths]):
            continue

        if any ([f not in line for f in [' score ', ' pv ', ' depth ']]):
            continue

        depth = line.split(' depth ')[1].split()[ 0]
        score = line.split(' score ')[1].split()[:2]
        move  = line.split(' pv '   )[1].split()[ 0]

        table[int(depth)].append((move, score))

    return table

def main():

    for player in PLAYERS:

        files = list(filter(lambda x: x.endswith('.pgn'), os.listdir(player)))

        chunks = [
            [files[x] for x in range(f, len(files), THREADS)]
            for f in range(THREADS)
        ]

        workers = [
            multiprocessing.Process(
                target=process_pgns,
                args=(player, chunks[f], ENGINE))
            for f in range(THREADS)
        ]

        for worker in workers: worker.start()
        for worker in workers: worker.join()

if __name__ == '__main__':
    main()

