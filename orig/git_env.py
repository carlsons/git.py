#! /usr/bin/python

''' this module defines some global variables for the g.py tool '''

import sys
import os.path

ScriptBasename    = os.path.split( sys.argv[0] )[1]
ScriptVersion     = '0.1-2015.05.26-01'

ScriptUsageText   = '''usage: {SCRIPT} [options [...]] command [args]
Git wrapper script, version {VERSION}

   options:

      -h|--help         : this text
      --version         : script version

      --verbose         : show detail while processing
'''

ScriptVersionText = '''{SCRIPT}: Git wrapper script (Python), version {VERSION}'''

ScriptBarfText    = '''{SCRIPT}: {0}'''

ScriptEnv         = {
   'SCRIPT'       : ScriptBasename,
   'VERSION'      : ScriptVersion
}
