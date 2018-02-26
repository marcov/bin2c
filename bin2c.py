#!/usr/bin/python3
#
# file: bin2c.py
# Author: cyberstorm
# License: GPLv2
#
# Usage: bin2c.py <list of files to convert>
#

import sys


class Bin2C:
    WRAP_WIDTH = 80

    def __init__(self):
        self.openedfiles = []


    def goToExit(self, retcode):
      for f in self.openedfiles:
        f.close()
      sys.exit(retcode)


    def normalizeFileName(self, inputFile):
      outputName = inputFile.split("/")[-1]

      for c in inputFile:
        if (ord(c) < ord("0")) or \
           (ord(c) > ord("9") and ord(c) < ord("A")) or \
           (ord(c) > ord("Z") and ord(c) < ord("a")) or \
           (ord(c) > ord("z")) :
           outputName = outputName.replace(c, "_")

      return outputName


    def convertSingleFile(self, f, inputFile, outputDir=".", varAttribute="", genHexStr=False, includeFiles=[]):

      nameStr = self.normalizeFileName(inputFile)
      wrap_ctr = 0
      cFile = None
      hFile = None

      cFileStr = outputDir + "/" + nameStr + ".c"
      hFileStr = outputDir + "/" + nameStr + ".h"

      try:
        cFile = open(cFileStr, "w")
      except IOError as e:
        print("Cannot create files: {:s}".format(cFileStr))
        print("Error code: " + str(e.errno) + ": " + e.strerror)
        self.goToExit(-1)

      try:
        hFile = open(hFileStr, "w")
      except IOError as e:
        print("Cannot create files: {:s}".format(hFileStr))
        print("Error code: " + str(e.errno) + ": " + e.strerror)
        self.goToExit(-1)

      self.openedfiles.append(cFile)
      self.openedfiles.append(hFile)

      f.seek(0)
      fileContent = f.read()

      cFile.write("#include \"%s.h\"\n" % nameStr)

      for f in includeFiles:
        cFile.write("#include \"%s\"\n" % f)

      cFile.write("\n\n")

      hFile.write("#ifndef __%s_H__" % nameStr.upper())
      hFile.write("\n")
      hFile.write("#define __%s_H__" % nameStr.upper())
      hFile.write("\n\n")

      hFile.write("extern const unsigned  %s_size; \n" % nameStr)
      cFile.write("const unsigned  %s_size = %s; \n" % (nameStr, len(fileContent)))

      if genHexStr:
        hFile.write("extern const unsigned char * %s; \n" % nameStr)
        cFile.write("const unsigned char * %s " % nameStr)

        if varAttribute != "":
            cFile.write("%s " % varAttribute)

        cFile.write("=\n\"")
      else:
        hFile.write("extern const unsigned char %s[]; \n" % nameStr)
        cFile.write("const unsigned char %s[] " % nameStr)

        if varAttribute != "":
            cFile.write("%s " % varAttribute)

        cFile.write("= {\n")

      for c in fileContent:

        if (sys.version_info < (3, 0)):
            c = ord(c)

        if genHexStr:
            chk = "\\x{:02X}".format(c)
            # no wrap for hex str
            #wrap_ctr += 4
        else:
            chk ="0x{:02X}, ".format(c)
            wrap_ctr += 6

        cFile.write(chk)

        if wrap_ctr >= self.WRAP_WIDTH:
            wrap_ctr = 0
            cFile.write("\n")

      if genHexStr:
        cFile.write("\";\n\n")
      else:
        cFile.write("};\n\n")

      hFile.write("\n#endif")


    def run(self, opts):


        for filename in opts.filesList:
            try:
                f = open(filename, "rb")
                self.openedfiles.append(f)
                print("Converting file %s..." % filename)
                self.convertSingleFile(f, filename, opts.outputDir, opts.varAttribute, opts.genHexStr, opts.includeFiles)
                f.close()
                self.openedfiles.remove(f)
                print("Done.")
            except IOError:
                print("Cannot open %s" % filename)
                self.goToExit(-1)



class Options():
    genHexStr = False
    varAttribute = ""
    filesList = []
    outputDir = "."
    includeFiles = []



def usageAndExit(exitCode):
    print("Usage: ")
    print("  " + sys.argv[0] + " [OPTIONS] <space-separated list of files to convert>")
    print("Options:")
    print("  -h:                            display this help")
    print("  --attribute <attribute value>: append to the variable definition the given attribute")
    print("  --literal:                     generate a constant pointer to a string literal instead of an array of unsigned chars")
    print("  --out <dirname>:               Create output files in the specified output directory")
    print("  --include <headerfile>:        Generate code '#include \"headerfile\"' (specify the option multiple times for multiple header files)")
    print("")
    sys.exit(exitCode)



def parseOptions(args):
    opts = Options()
    while len(args) > 0:
        curr = args.pop(0)

        if curr == '-h' or curr == '--help':
            usageAndExit(0)

        elif curr == '--attribute':
            opts.varAttribute = args.pop(0)
            print("Detected attribute with value: " + opts.varAttribute)

        elif curr == '--literal':
            opts.genHexStr = True
            print("Generating an hex string instead of an array of hex")

        elif curr == "--out":
            opts.outputDir = args.pop(0)
            print("Output files will be put in: " + opts.outputDir)

        elif curr == "--include":
            incFile = args.pop(0)
            opts.includeFiles.append(incFile)
            print("Extra include detected: " + incFile)

        elif curr[0] == '-':
            print("Unknown option: " + curr)
            usageAndExit(-1)

        else:
            # This is the list of input files
            opts.filesList.append(curr)
            print("Detected input file: " + curr)

    if len(opts.filesList) == 0:
        print("No input files specified!")
        usageAndExit(-1)

    print("Param checking done")
    return opts


def main():
    options = parseOptions(sys.argv[1:])
    print("")
    bin2c = Bin2C()
    bin2c.run(options)

    bin2c.goToExit(0)

if __name__ == "__main__":
  # execute only if run as a script
  main()

