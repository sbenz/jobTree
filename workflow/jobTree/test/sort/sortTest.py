#!/usr/bin/env python
"""Tests the scriptTree jobTree-script compiler.
"""

import unittest
import sys
import os
import random

from workflow.jobTree.lib.bioio import TestStatus
from workflow.jobTree.lib.bioio import parseSuiteTestOptions
from workflow.jobTree.lib.bioio import system
from workflow.jobTree.lib.bioio import getTempDirectory
from workflow.jobTree.lib.bioio import getTempFile

from workflow.jobTree.test.sort.lib import merge, sort, copySubRangeOfFile, getMidPoint

class TestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.testNo = TestStatus.getTestSetup(1, 2, 10, 10)
    
    def testScriptTree_SortSimple(self):
        """Tests scriptTree/jobTree by sorting a file in parallel.
        """
        scriptTree_SortTest(self.testNo, "single_machine")
    
    def testScriptTree_SortGridEngine(self):
        """Tests scriptTree/jobTree by sorting a file in parallel.
        """
        scriptTree_SortTest(self.testNo, "gridengine")
    
    def testScriptTree_SortAcid(self):
        """Tests scriptTree/jobTree by sorting a file in parallel.
        """
        scriptTree_SortTest(self.testNo, "acid_test")

#The following functions test the functions in the test!
    
    def testSort(self):
        for test in xrange(self.testNo):
            tempDir = getTempDirectory(os.getcwd())
            tempFile1 = getTempFile(rootDir=tempDir)
            makeFileToSort(tempFile1)
            lines1 = loadFile(tempFile1)
            lines1.sort()
            sort(tempFile1)
            lines2 = loadFile(tempFile1)
            checkEqual(lines1, lines2)
            system("rm -rf %s" % tempDir)
    
    def testMerge(self):
        for test in xrange(self.testNo):
            tempDir = getTempDirectory(os.getcwd())
            tempFile1 = getTempFile(rootDir=tempDir)
            tempFile2 = getTempFile(rootDir=tempDir)
            tempFile3 = getTempFile(rootDir=tempDir)
            makeFileToSort(tempFile1)
            makeFileToSort(tempFile2)
            sort(tempFile1)
            sort(tempFile2)
            merge(tempFile1, tempFile2, tempFile3)
            lines1 = loadFile(tempFile1) + loadFile(tempFile2)
            lines1.sort()
            lines2 = loadFile(tempFile3)
            checkEqual(lines1, lines2)
            system("rm -rf %s" % tempDir)
    
    def testCopySubRangeOfFile(self):
        for test in xrange(self.testNo):
            tempDir = getTempDirectory(os.getcwd())
            tempFile = getTempFile(rootDir=tempDir)
            outputFile = getTempFile(rootDir=tempDir)
            makeFileToSort(tempFile)
            fileSize = os.path.getsize(tempFile)
            assert fileSize > 0
            fileStart = random.choice(xrange(0, fileSize))
            fileEnd = random.choice(xrange(fileStart, fileSize))
            copySubRangeOfFile(tempFile, fileStart, fileEnd, outputFile)
            l = open(outputFile, 'r').read()
            l2 = open(tempFile, 'r').read()[fileStart:fileEnd]
            checkEqual(l, l2)
            system("rm -rf %s" % tempDir)
            
    def testGetMidPoint(self):
        for test in xrange(self.testNo):
            tempDir = getTempDirectory(os.getcwd())
            tempFile = getTempFile(rootDir=tempDir)
            makeFileToSort(tempFile)
            l = open(tempFile, 'r').read()
            fileSize = os.path.getsize(tempFile)
            midPoint = getMidPoint(tempFile, 0, fileSize)
            print "the mid point is %i of a file of %i bytes woth byte" % (midPoint, fileSize)
            assert midPoint < fileSize
            assert l[midPoint] == '\n'
            assert midPoint >= 0
            system("rm -rf %s" % tempDir)
            
def scriptTree_SortTest(testNo, batchSystem, lines=100000, maxLineLength=10, N=1000):
    """Tests scriptTree/jobTree by sorting a file in parallel.
    """
    for test in xrange(testNo):
        tempDir = getTempDirectory(os.getcwd())
        tempFile = getTempFile(rootDir=tempDir)
        jobTreeDir = os.path.join(tempDir, "jobTree")
        makeFileToSort(tempFile, lines=lines, maxLineLength=maxLineLength)
        #First make our own sorted version
        fileHandle = open(tempFile, 'r')
        l = fileHandle.readlines()
        l.sort()
        fileHandle.close()
        #Sort the file
        command = "scriptTreeTest_Sort.py --jobTree %s --logLevel=DEBUG --fileToSort=%s --N %i --batchSystem %s --jobTime 1.0" % (jobTreeDir, tempFile, N, batchSystem)
        system(command)
        #Now check the file is properly sorted..
        #Now get the sorted file
        fileHandle = open(tempFile, 'r')
        l2 = fileHandle.readlines()
        fileHandle.close()
        checkEqual(l, l2)
        system("rm -rf %s" % tempDir)
            
def checkEqual(one, two):
    if one != two:
        print "one", one
        print "two", two
    assert one == two
        
def loadFile(file):
    fileHandle = open(file, 'r')
    lines = fileHandle.readlines()
    fileHandle.close()
    return lines
            
def getRandomLine(maxLineLength):
    return "".join([ random.choice([ 'a', 'c', 't', 'g', "A", "C", "G", "T", "N", "X", "Y", "Z" ]) for i in xrange(maxLineLength) ]) + "\n"

def makeFileToSort(fileName, lines=10, maxLineLength=10):
    fileHandle = open(fileName, 'w')
    for line in xrange(lines):
        fileHandle.write(getRandomLine(maxLineLength))
    fileHandle.close()
                   
def main():
    parseSuiteTestOptions()
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()