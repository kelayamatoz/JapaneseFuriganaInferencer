# -*- coding: utf-8 -*-

import codecs

import util
import model

class TestCase:
    def __init__(self, line):
        self.word, self.pronunciation = line.split()
        self.mapping = {}
        partition = self.pronunciation.split(',')
        self.pronunciation = ''.join(partition)
        for index, kanji in enumerate(self.word):
            self.mapping[kanji] = partition[index]
        self.model = None

    def test(self, model):
        self.model = model

        self.beliefs = []
        self.partitions = util.generatePossiblePartitions(self.word, self.pronunciation)
        for p in self.partitions:
            prop = 1.0
            for k, f in p:
                if k in model:
                    prop *= model[k].prob(f)
            self.beliefs.append(prop)
        util.normalize_vector(self.beliefs)

        heuritics = util.omegaHeuristics(self.partitions)

        beliefMatrix = sorted([(belief, heuritics[i], i) for i, belief in enumerate(self.beliefs)], reverse=True)
        self.bestPartition = self.partitions[beliefMatrix[0][2]]
        if len(beliefMatrix) == 1:
            self.confidence = 10.0
        else:
            self.confidence = beliefMatrix[0][0] - beliefMatrix[1][0]

        self.correctAnswer = True
        for k, f in self.bestPartition:
            if self.mapping[k] != f:
                self.correctAnswer = False
                break


    def baseline_test(self):
        self.partitions = util.generatePossiblePartitions(self.word, self.pronunciation)
        self.beliefs = util.omegaHeuristics(self.partitions)
        util.normalize_vector(self.beliefs)

        beliefMatrix = sorted([(belief, i) for i, belief in enumerate(self.beliefs)], reverse=True)
        self.bestPartition = self.partitions[beliefMatrix[0][1]]
        if len(beliefMatrix) == 1:
            self.confidence = 10.0
        else:
            self.confidence = beliefMatrix[0][0] - beliefMatrix[1][0]

        self.correctAnswer = True
        for k, f in self.bestPartition:
            if self.mapping[k] != f:
                self.correctAnswer = False
                break


    def __str__(self):
        verdict = 'CORRECT' if self.correctAnswer else 'WRONG'
        outputStr = u'<%s> --- (%s %s) ---\n' % (verdict, self.word, self.pronunciation)
        for i, p in enumerate(self.partitions):
            beliefStr = '%.1f' % self.beliefs[i]
            bestPartitionIndicator = ' '
            if self.bestPartition == p:
                bestPartitionIndicator = '>'
            def _converter(t):
                kanji, furigana = t
                if not self.model:
                    return '%s:%s' % (kanji, furigana) 
                probStr = '-'
                if kanji in self.model:
                    probStr = '%.1f' % (self.model[kanji].prob(furigana) * 100.0)
                return '%s:%s(%s)' % (kanji, furigana, probStr)
            outputStr += u' %s[%6s] %s\n' % (bestPartitionIndicator, beliefStr, u' '.join(map(_converter, p)))
        outputStr += 'Confidence = %.3f\n' % (self.confidence)
        return outputStr


def _buildTestStatistics(allTestCases):
    nTestCases = 0
    nCorrectTestCases = 0
    totalConfidence = 0

    for testcase in allTestCases:
        nTestCases += 1
        if testcase.correctAnswer:
            nCorrectTestCases += 1
            totalConfidence += testcase.confidence
        else:
            totalConfidence -= testcase.confidence * 3.0

    return (nTestCases, nCorrectTestCases, totalConfidence)


def _performTesting(model, writeResults=False):
    with codecs.open('test.txt', 'r', encoding='utf-8') as f:
        def _converter(line):
            return TestCase(line)
        allTestCases = map(_converter, f.readlines())

    for testcase in allTestCases:
        testcase.test(model)

    nTestCases, nCorrectTestCases, totalConfidence = _buildTestStatistics(allTestCases)

    if writeResults:
        with codecs.open('test_result.txt', 'w', encoding='utf-8') as f:
            for testcase in allTestCases:
                f.write(unicode(testcase) + u'\n')

    return (nTestCases, nCorrectTestCases, totalConfidence)


lastConfidence = None
def testModel(model, output=True):
    nTestCases, nCorrectTestCases, totalConfidence = _performTesting(model, writeResults=True)
    print 'Correct: %d/%d (%.1f%%)' % (nCorrectTestCases, nTestCases, float(nCorrectTestCases) / nTestCases * 100.0)
    
    global lastConfidence
    confidenceCmp = ''
    if lastConfidence:
        confidenceCmp = '(%+.3f)' % (totalConfidence - lastConfidence)
    print 'Confidence: %.3f %s' % (totalConfidence, confidenceCmp)
    lastConfidence = totalConfidence


logFileInitialized = False
def continuousTesting(model, trialID, tupleID):
    nTestCases, nCorrectTestCases, totalConfidence = _performTesting(model, writeResults=False)

    global logFileInitialized
    if not logFileInitialized:
        with open("test_log.txt", "w") as f:
            f.write('==== Continuous Performance Testing Log ====\n')
        logFileInitialized = True
    
    with open("test_log.txt", "a") as f:
        f.write('%d %d %.1f%% %.3f\n' % (trialID, tupleID, float(nCorrectTestCases) / nTestCases * 100.0, totalConfidence))


def testWordPartition():
    alltuples = []

    with codecs.open('tuples.txt', 'r', encoding='utf-8') as f:
        def _converter(line):
            kanji, furigana = line.split()
            return (kanji, furigana)
        alltuples = map(_converter, f.readlines())

    for kanji, furigana in alltuples:
        partitions = util.generatePossiblePartitions(kanji, furigana)
        print u'--- (%s %s) ---' % (kanji, furigana)
        for p in partitions:
            print ' '.join(map(lambda t: '%s:%s' % (t[0], t[1]), p))
        print

def testBaselineAlgorithm():
    with codecs.open('test.txt', 'r', encoding='utf-8') as f:
        def _converter(line):
            return TestCase(line)
        allTestCases = map(_converter, f.readlines())

    nTestCases = 0
    nCorrectTestCases = 0
    totalConfidence = 0

    for testcase in allTestCases:
        testcase.baseline_test()

    nTestCases, nCorrectTestCases, totalConfidence = _buildTestStatistics(allTestCases)

    print 'Correct: %d/%d (%.1f%%)' % (nCorrectTestCases, nTestCases, float(nCorrectTestCases) / nTestCases * 100.0)
    print 'Confidence: %.3f' % totalConfidence

    with codecs.open('baseline_test_result.txt', 'w', encoding='utf-8') as f:
        for testcase in allTestCases:
            f.write(unicode(testcase) + u'\n')


if __name__ == "__main__":
    # testWordPartition()
    testBaselineAlgorithm()


