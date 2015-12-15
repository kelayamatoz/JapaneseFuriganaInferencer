# -*- coding: utf-8 -*-

import re

def isHiragana(char):
    return re.search(ur'[\u3041-\u3094]', char) != None

AUX_HIRAGANA_SET = set([u'ゃ', u'ゅ', u'ょ', u'っ', u'ん'])
def isAuxHiragana(char):
    return char in AUX_HIRAGANA_SET

def isLegalFurigana(str):
    return not isAuxHiragana(str[0]) 

'''
Furigana heuristics calculate the possibility of the furigana of a single
kanji based on observation of Japanese language.
In general, the furigana of a kanji should be of 1 or 2 syllabi. 
(for example じょう has 3 characters but has only 2 syllabi)
The longer the furigana is, the more unlikely it can be.
Length    | Heuristic Value
1.0         1.0
2.0         1.0
3.0         0.33
4.0         0.19
5.0         0.12
'''
NON_OCCUPYING_HIRAGANA_SET = set([u'ゃ', u'ゅ', u'ょ'])
def furiganaHeuristics(furigana):
    length =  len(filter(lambda c: c not in NON_OCCUPYING_HIRAGANA_SET, furigana))
    if length <= 2:
        return 1.0
    else:
        return 3.0 / length ** 2

def generatePossiblePartitions(kanji, furigana):

    partitions = []

    def _search(partial, kanji, furigana):
        if isHiragana(kanji[0]):
            if kanji[0] == furigana[0]:
                _search(partial, kanji[1:], furigana[1:])
            return  

        if len(kanji) == 1:
            if isLegalFurigana(furigana):
                partial.append((kanji, furigana))
                partitions.append(partial)
            return

        for untilIndex in range(len(furigana) - len(kanji) + 1):
            if isLegalFurigana(furigana[:untilIndex + 1]):
                extendedPartial = list(partial)
                extendedPartial.append((kanji[0], furigana[:untilIndex + 1]))
                _search(extendedPartial, kanji[1:], furigana[untilIndex + 1:])

    _search(list(), kanji, furigana)

    return partitions

def omegaHeuristics(partitions):
    omegas = []
    for p in partitions:
        omega = 0.0;
        for k, f in p:
            omega += furiganaHeuristics(f)
        omegas.append(omega)
    return normalize_vector(omegas)


def normalize(distribution):
    # normalize probability distribution
    totalProb = sum([v for k, v in distribution.iteritems()])
    keysToRemove = []
    for k in distribution.iterkeys():
        distribution[k] /= totalProb

        # remove entries with probability < 0.1%
        if distribution[k] < 1e-3:
            keysToRemove.append(k)

    for k in keysToRemove:
        del distribution[k]

    return distribution


def normalize_vector(vector, maximum = 10.0):
    maxEntry = max(vector)
    scale = maximum / maxEntry
    for i, p in enumerate(vector):
        vector[i] = p * scale
    return vector


def addDistribution(d1, d2, weight = 1.0):
    # add the probability distribution d2 into d1 (no normalization provided)
    for k in d2.iterkeys():
        if k in d1:
            d1[k] += d2[k] * weight
        else:
            d1[k] = d2[k] * weight

def isSameDistribution(d1, d2):
    for k in set(d1.iterkeys()) | set(d2.iterkeys()):
        if abs(d1.get(k, 0.0) - d2.get(k, 0.0)) > 1e-6:
            return False
    return True


