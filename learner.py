# -*- coding: utf-8 -*-

import codecs
import random
import sys

import util
from model import *
from test import testModel, continuousTesting

nodeMap = {}
allFactors = []


def learn(trial, tuples, testingInterval=None):

    print ' ** Start trial %d:' % trial

    def construct():
        newFactor = Factor(kanji, furigana, nodeMap)
        allFactors.append(newFactor)
        for k in newFactor.allKanji:
            if k not in nodeMap:
                nodeMap[k] = Node(k, newFactor.furiganaSetForKanji(k))
            nodeMap[k].factors.append(newFactor)
        return newFactor

    def infer(factor):
        MAX_ITERATION = 30
        update_queue = set(factor.allKanji)
        iteration = 0
        while update_queue and iteration < MAX_ITERATION:
            kanji = random.choice(list(update_queue))
            update_queue.remove(kanji)
            node = nodeMap[kanji]
            if node.updateDistribution():
                update_queue.update(node.allAdjacentKanjis())
            iteration += 1

    progress = 0

    if trial > 0:
        for node in nodeMap.itervalues():
            node.resetDistribution()

    for i, (kanji, furigana) in enumerate(tuples):
        if trial == 0:
            # have to construct necessary nodes and factors for the initial trial
            factor = construct()
        else:
            factor = allFactors[i]

        infer(factor)  

        progress += 1
        if testingInterval and (progress % testingInterval == 0): 
            continuousTesting(nodeMap, trial, progress)

        percentage = float(progress) / len(tuples) 
        sys.stdout.write('\r')
        sys.stdout.write('  LEARNING [%-30s] %.1f%%' % ('=' * int(percentage * 30), percentage * 100))
        sys.stdout.flush()


    print '\n ** Finish trial %d.' % trial


def adjustParameters():
    # always update omega before update alpha because the calculation of alpha is dependent
    # upon the lateset value of omega

    for factor in allFactors:
        factor.updateWeightVectorOmega()
    
    for node in nodeMap.itervalues():
        node.updateWeightVectorAlpha()

    print 'Updated weight vectors omega and alpha.'


def outputResult(trial, distribution=True, partitions=True, alphas=True):

    def outputAllNodeDistributions():    
        with codecs.open('result/distribution_%d.txt' % trial, 'w', encoding='utf-8') as f:
            for node in nodeMap.itervalues():
                f.write(unicode(node) + u'\n')

    def outputAllFactorPartitions():
        with codecs.open('result/partitions_%d.txt' % trial, 'w', encoding='utf-8') as f:
            for factor in allFactors:
                f.write(unicode(factor) + u'\n')

    def outputAllAlphaVectors():
        with codecs.open('result/alphas_%d.txt' % trial, 'w', encoding='utf-8') as f:
            for node in nodeMap.itervalues():
                f.write(unicode(node.outputAlphaVector()) + u'\n')

    if distribution:    outputAllNodeDistributions()
    if partitions:      outputAllFactorPartitions()
    if alphas:          outputAllAlphaVectors()


if __name__ == "__main__":

    alltuples = []
    with codecs.open('tuples.txt', 'r', encoding='utf-8') as f:
        def _converter(line):
            kanji, furigana = line.split()
            return (kanji, furigana)
        alltuples = map(_converter, f.readlines())

    print ' ** Training set contains %d tuples.' % (len(alltuples))

    TOTAL_TRIAL = 3
    for trial in range(TOTAL_TRIAL):
        learn(trial, alltuples)
        adjustParameters()
        outputResult(trial)

        print ' ** Start testing:'
        testModel(nodeMap)

    print ' ** All done. Output written to files.'

