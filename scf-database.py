#!/usr/bin/env python
import glob
import os
import numpy
from scipy import stats

method = "complex X2CHF"
basis  = "6-31G"
nsmp   = "1"
mem    = "1GB"
scfOptions = "[SCF]\ndiis=true\nnKeep=20\nmaxIter=10000\ndamp=false\nfdcTol=1E-4\n"

chronus = "/home/agrofe/chronusq_source/dev/chronusq_dev/build/chronusq"    

geomFiles  = glob.glob('./test-cases/**/*.txt',recursive=True)
if len(geomFiles) == 0:
    print("Found no geometry files")
    quit()

def createInputFile(inpFileName,geomFileName,method,basis,nsmp,mem,scfOptions):
    print(geomFileName)
    inputText = "[Molecule]\n"
    with open(geomFileName,'r') as geomFile:
        inputText += geomFile.read()
    inputText += "[QM]\nreference="+ method + "\njob=scf\n"
    inputText += scfOptions
    inputText += "[BASIS]\nbasis=" + basis + "\n"
    inputText += "[MISC]\nnsmp=" + nsmp + "\nmem=" + mem + "\n"

    with open(inpFileName,'w') as inpFile:
        inpFile.write(inputText)

def runInputFile(inpFileName,outFileName,exe):
    binFile = inpFileName.replace(".inp",".bin")
    status = os.system(exe + " -i " + inpFileName  + " -b " + binFile + " -o " + outFileName + " 2>/dev/null")
    os.remove(binFile)
    os.remove(inpFileName)
    outputText = ""
    with open(outFileName,'r') as outFile:
        outputText += outFile.read()
    return [outputText,status]

def parseOutput(outText):
    lines = outText.split("\n")
    scfData = [];
    for l in lines:
        words = l.split();
        if len(words) > 3 and  words[0] == "SCFIt:":
            scfData.append(words[1:])
    return numpy.transpose(numpy.array(scfData))

def printDataSet(dataSet):
    numpy.set_printoptions(linewidth=numpy.inf)
    fNames = dataSet.keys()
    for f in fname:
        string = f + ":\n"
        print(string)
        print(dataSet[f])
        string = "\n\n"
        print(string)

def printHistogram(hist,bins):
    i = 0
    for h in hist:
        print("{a:10.2f}".format(a = bins[i]), end='')
        print(":",end='')
        for x in range(h):
            print("+",end='')
        print()
        i += 1

def prettyPrintData(header,x,y,formatStr):
    i = 0
    nMax = min(len(x),len(y))
    print(header+":")
    for i in range(nMax):
        print(formatStr.format(a = x[i], b = y[i] ) )
        i += 1
    print("\n")

dataSet = {}
failedFiles = [];
for f in geomFiles:
    createInputFile("test.inp",f,method,basis,nsmp,mem,scfOptions)

    status = 0
    outText = ""
    outputFile = f.replace(".txt",".out")
    [outText, status] = runInputFile("test.inp",outputFile,chronus)
    if status != 0:
        failedFiles.append(f)
    dataSet[f] = parseOutput(outText)
print("\n")

if len(failedFiles) > 0:
    print("Failed Runs:")
    for f in failedFiles:
       print("   " + f)
    print("\n")

#print("Number of SCF Iterations:")
scfIter = numpy.arange(len(dataSet))
i = 0
for f in geomFiles:
    scfIter[i] = dataSet[f][0].size
    i += 1
#print()
prettyPrintData("Number of SCF Iterations",list(dataSet.keys()),scfIter,"{a:50}{b:10}")

stats = stats.describe(scfIter)
print(stats)
print()

[hist,bins] = numpy.histogram(scfIter)
prettyPrintData("Histogram",bins,hist,"{a:10.2f}{b:10}")
printHistogram(hist,bins)
