#! /usr/bin/python

''' this module defines some global helper functions for the g.py tool '''

from   git_env     import *

def barf( text ):
   print ScriptBarfText.format( text,  **ScriptEnv )

def showUsage():
   print ScriptUsageText.format(       **ScriptEnv )

def showVersion():
   print ScriptVersionText.format(     **ScriptEnv )

