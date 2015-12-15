# -*- coding: utf-8 -*-

import os
import codecs
import re
import random

import util

alllines = []

for _file in os.listdir("corpus"):
    if _file.endswith(".txt") and not _file.startswith('_'):
        print 'Load file %s' % _file
        with codecs.open("corpus/%s" % _file, 'r', encoding='utf-8') as f:
            alllines.extend(f.readlines())

alltuples = []

for line in alllines:
    kanji, furigana = line.split()

    # remove words with duplicate notations
    index = kanji.find(u'々')
    if index != -1: continue

    # remove parts of kanji and furigana that are the same
    while kanji and kanji[0] == furigana[0]:
        kanji = kanji[1:]
        furigana = furigana[1:]
    while kanji and kanji[-1] == furigana[-1]:
        kanji = kanji[:-1]
        furigana = furigana[:-1]

    if kanji:
        alltuples.append((kanji, furigana))

print 'Total number of tuples: %d.' % len(alltuples)

with codecs.open('tuples.txt', 'w', encoding='utf-8') as f:
    for kanji, furigana in alltuples:
        f.write(u'%s %s\n' % (kanji, furigana))

if not os.path.isfile('test.txt'):
    sampleSize = 100
    multipleKanjiTuples = filter(lambda tp: len(tp[0]) > 1, alltuples)
    sample = random.sample(multipleKanjiTuples, sampleSize)
    print 'Randomly sample %d tuples (out of %d) as test set.' % (sampleSize, len(multipleKanjiTuples))
    with codecs.open('test.txt', 'w', encoding='utf-8') as f:
        for kanji, furigana in sample:
            f.write(u'%s %s\n' % (kanji, furigana))

