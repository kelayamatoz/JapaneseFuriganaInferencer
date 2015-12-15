
import util
from collections import Counter

'''
A node represents a kanji variable in the factor graph.
It is initialized by the kanji and its possible furiganas (domain).
'''
class Node:
    def __init__(self, kanji, furigana_set):
        self.kanji = kanji
        self.factors = []

        # default distribution
        self.distribution = {}
        numFurigana = len(furigana_set)
        for f in furigana_set:
            self.distribution[f] = 1.0 / numFurigana

        self.alphas  = []
        self.probSmoothing = 0.1

    def __str__(self):
        outputStr = u'%s: ' % (self.kanji)
        distributionList = sorted([(v, k) for k,v in self.distribution.iteritems()], reverse=True)
        outputStr += u' '.join([u'%s(%.1f)' % (furigana, prob * 100) for prob, furigana in distributionList])
        return outputStr

    def outputAlphaVector(self):
        alphaVector = []
        for i, factor in enumerate(self.factors):
            alphaVector.append((self.alphas[i], u'%s %s' % (factor.word, factor.pronunciation)))
        alphaVector.sort(reverse=True)
        outputStr = u'%s: ' % (self.kanji)
        outputStr += u' '.join(['%.1f (%s)' % (alpha, factorStr) for alpha, factorStr in alphaVector])
        return outputStr

    def prob(self, furigana):
        if furigana in self.distribution:
            return self.distribution[furigana]
        else:
            return self.probSmoothing  # Laplace smoothing for non-existent furigana

    def updateDistribution(self):
        distribution = {}
        if self.alphas:
            for i, factor in enumerate(self.factors):
                util.addDistribution(distribution, factor.newDistributionForKanji(self.kanji), weight=self.alphas[i])
        else:
            for factor in self.factors:
                util.addDistribution(distribution, factor.newDistributionForKanji(self.kanji))

        util.normalize(distribution)
        if not util.isSameDistribution(self.distribution, distribution):
            self.distribution = distribution
            return False
        return True  # indicate that updates have been made

    def allAdjacentKanjis(self):
        kanji_set = set()
        for factor in self.factors:
            kanji_set.update(factor.allKanji)
        kanji_set.remove(self.kanji)
        return kanji_set

    def updateWeightVectorAlpha(self):
        self.alphas = []
        furiganas = []
        for factor in self.factors:
            furiganas.extend(factor.mostProbableFuriganas(self.kanji))
        furigana_counter = Counter(furiganas)
        for factor in self.factors:
            alpha = 0.0
            for f in factor.mostProbableFuriganas(self.kanji):
                alpha += 1.0 / (furigana_counter[f] + 1)
            self.alphas.append(alpha)

        util.normalize_vector(self.alphas)

    def resetDistribution(self):
        furigana_set = set(filter(lambda key: self.distribution[key] > 0.01, self.distribution.iterkeys()))
        numFurigana = len(furigana_set)
        self.distribution = {}
        for f in furigana_set:
            self.distribution[f] = 1.0 / numFurigana
        self.probSmoothing = 0.001

'''
A factor represents a constraint between nodes in the factor graph.
It is initialized by a tuple of (word, pronunciation) in the training data.
'''
class Factor:
    def __init__(self, kanji, furigana, verticesMap):
        self.word = kanji
        self.pronunciation = furigana

        self.partitions = util.generatePossiblePartitions(kanji, furigana)
        self.allKanji = []
        for k, _ in self.partitions[0]:
            self.allKanji.append(k)

        self._verticesMap = verticesMap  # store a pointer to the the map of all vertices 
        self.omegas = []
        # self.omegas = util.omegaHeuristics(self.partitions)
        self.bestPartition = None

    def __str__(self):
        outputStr = u'--- (%s %s) ---\n' % (self.word, self.pronunciation)
        for i, p in enumerate(self.partitions):
            omegaStr = u'-'
            if self.omegas:
                omegaStr = '%.1f' % self.omegas[i]
            bestPartitionIndicator = ' '
            if self.bestPartition == p:
                bestPartitionIndicator = '>'
            outputStr += u' %s[%6s] %s\n' % (bestPartitionIndicator, omegaStr, u' '.join(map(lambda t: '%s:%s' % (t[0], t[1]), p)))
        return outputStr


    def furiganaSetForKanji(self, kanji):
        furigana_set = set()
        for p in self.partitions:
            for k, f in p:
                furigana_set.add(f)
        return furigana_set

    def newDistributionForKanji(self, kanji):
        distribution = {}
            
        if len(self.allKanji) == 1:
            furigana_set = self.furiganaSetForKanji(kanji)
            numFurigana = len(furigana_set)
            for f in furigana_set:
                distribution[f] = 1.0 / numFurigana

        else:
            # k is the kanji whose probability will be marginalized out
            for kIndex, k in enumerate(self.allKanji):
                if kanji == k:

                    # for all possible partitions p for the current factor
                    for pIndex, p in enumerate(self.partitions):

                        # the probability will be the join probability of
                        # all other kanjis having the furigana specified 
                        # by the particular partition
                        prob = 1.0
                        for index in range(len(p)):
                            if index != kIndex:
                                k0, f0 = p[index]
                                prob *= self._verticesMap[k0].prob(f0)

                        if self.omegas:
                            prob *= self.omegas[pIndex]

                        furigana = p[kIndex][1]
                        if furigana not in distribution:
                            distribution[furigana] = prob
                        else:
                            distribution[furigana] += prob

        # return the normalized distribution for a kanji respect to one
        # specific factor
        return util.normalize(distribution)

    # the best partition predicted after one trial might not necessarily
    # be correct, add smoothing factor to give some chance to other possible
    # partitions in the next round
    def updateWeightVectorOmega(self, smoothing = 0.5):
        self.omegas = []
        for p in self.partitions:
            prop = 1.0
            for k, f in p:
                prop *= (self._verticesMap[k].prob(f) + smoothing)
            self.omegas.append(prop)
        util.normalize_vector(self.omegas)

        # find the most probable partition
        _, index = max([(omega, i) for i, omega in enumerate(self.omegas)])
        self.bestPartition = self.partitions[index]

    def mostProbableFuriganas(self, kanji):
        furiganas = list()
        for k, f in self.bestPartition:
            if k == kanji:
                furiganas.append(f)
        return furiganas            



