#!/usr/bin/python

import glob
import os

geomFiles  = glob.glob('./test-cases/**/*.txt',recursive=True)

for f in geomFiles:
    os.remove(f);
