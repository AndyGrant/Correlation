#!/bin/python3

import requests, re, sys, os

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'
}

PlayerIDs = {
    '52948'  : 'Carlsen',
    '52629'  : 'Liren',
    '10084'  : 'Nakamura',
    '152611' : 'Niemann',
    '54683'  : 'Nepomniachtchi',
    '152702' : 'Firouzja',
    '95915'  : 'So',
    '107252' : 'Giri',
}

for player_id, player_name in PlayerIDs.items():

    if not os.path.isdir(player_name):
        os.mkdir(player_name)

    for page in range(1, 100):

        game_list = 'https://www.chessgames.com/perl/chess.pl?page=%d&pid=%s&playercomp=either&year=2020&yearcomp=ge'
        game_list = game_list % (page, player_id)
        data      = str(requests.get(url=game_list, headers=headers).content)
        game_ids  = [int(f) for f in re.findall('gid=([0-9]+)', data)]

        for game_id in set(game_ids):

            game_url = 'https://www.chessgames.com/perl/chessgame?gid=%d' % (game_id)
            data     = str(requests.get(url=game_url, headers=headers).content)
            download = re.findall('/nodejs/game/downloadGamePGN/(.*.pgn\?gid=[0-9]+)', data)[0]

            download_url = 'https://www.chessgames.com/nodejs/game/downloadGamePGN/%s'
            download_url = download_url % (download)

            r = requests.get(url=download_url, headers=headers)
            with open('%s/%d.pgn' % (player_name, game_id), 'w') as fout:
                fout.write(r.content.decode('utf-8'))
                print ('Saved PGN #%d for %s' % (game_id, player_name))

        if len(game_ids) == 0:
            break
