#!/bin/python3

import os, json, sys
import matplotlib.pyplot as plt

PLAYERS = ['Carlsen', 'Firouzja', 'Giri', 'Liren', 'Nakamura', 'Nepomniachtchi', 'Niemann', 'So']
DEPTHS  = [18]
ENGINES = ['Ethereal-13.00', 'Ethereal-13.25']

def analyze_game(blob):

    T1 = { depth : 0 for depth in DEPTHS }
    T2 = { depth : 0 for depth in DEPTHS }
    T3 = { depth : 0 for depth in DEPTHS }

    N = len(blob['played'])

    for played, analysis in zip(blob['played'], blob['analysis']):

        for depth in DEPTHS:

            multipvs = analysis[str(depth)]
            for T in range(min(3, len(multipvs))):
                T1[depth] += T == 0 and multipvs[T][0] == played
                T2[depth] += T == 1 and multipvs[T][0] == played
                T3[depth] += T == 2 and multipvs[T][0] == played

    for key, value in T1.items(): T1[key] = value / N
    for key, value in T2.items(): T2[key] = value / N
    for key, value in T3.items(): T3[key] = value / N

    return (T1, T2, T3)

for engine in ENGINES:

    print()

    for player in PLAYERS:

        T1_scores = []
        T2_scores = []
        T3_scores = []

        directory = 'Analysis/%s/' % (engine)
        for file in list(filter(lambda x: x.startswith(player), os.listdir(directory))):
            with open(os.path.join(directory, file)) as fin:

                # Skip extremely short games (error processing ?)
                blob = json.load(fin)
                if (len(blob['played']) < 10):
                    continue

                t1, t2, t3 = analyze_game(blob)
                T1_scores.append(t1); T2_scores.append(t2); T3_scores.append(t3);

        for depth in DEPTHS:

            t1 = [f[depth] for f in T1_scores]
            t2 = [f[depth] for f in T2_scores]
            t3 = [f[depth] for f in T3_scores]

            # fix, axs = plt.subplots(1, 3, sharex=True, sharey=True, tight_layout=True)
            #
            # plt.xticks([.0, .2, .4, .6, .8, 1.0])
            #
            # axs[0].hist(t1, bins=20, range=[0.0, 1.0])
            # axs[1].hist(t2, bins=20, range=[0.0, 1.0])
            # axs[2].hist(t3, bins=20, range=[0.0, 1.0])
            #
            # plt.savefig('%s.png' % (player))

            a_t1 = sum(t1) / len(t1)
            a_t2 = sum(t2) / len(t2)
            a_t3 = sum(t3) / len(t3)

            print ('%20s %20s: N=%4d T1=%5.3f T2=%5.3f T3=%5.3f TX=%5.3f'
                % (engine, player, len(t1), a_t1, a_t2, a_t3, sum([a_t1, a_t2, a_t3])))

            # t12  = [f1 + f2 for f1, f2 in zip(t1, t2)]
            # t123 = [f1 + f2 + f3 for f1, f2, f3 in zip(t1, t2, t3)]
            # print (engine, player, max(t1), max(t2), max(t3), max(t12), max(t123))
