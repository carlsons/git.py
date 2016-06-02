#! /usr/bin/python

''' this module implements the interface to the Python-based Git wrapper '''

import sys
import getopt
import exceptions

from   git_env     import *
from   git_include import *

import git
import cmdopts


ScriptOpts        = cmdopts.Options()
ScriptCmds        = cmdopts.Commands()

ScriptDefaultArgs = [ 'status' ]

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

GlobalEnv = cmdopts.Environ( 'global' )

GlobalEnv.add( cmdopts.EnvVar( 'SCRIPT',    value=ScriptBasename,   constant=True ) )
GlobalEnv.add( cmdopts.EnvVar( 'VERSION',   value=ScriptVersion,    constant=True ) )
GlobalEnv.add( cmdopts.EnvVar( 'repo_path', cmdopts.varPATH ) )
GlobalEnv.add( cmdopts.EnvFlag( 'verbose' ) )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# handler functions for options

def optHelp( env ):
   'show usage and syntax'
   showUsage()
   sys.exit(0)
ScriptOpts.addHandler( cmdopts.OptHandler(      [ '-h', '--help' ],     optHelp     ) )

def optVersion( env ):
   'show script version'
   showVersion()
   sys.exit(0)
ScriptOpts.addHandler( cmdopts.OptHandler(      [ '--version' ],        optVersion  ) )

ScriptOpts.addHandler( cmdopts.EnvVarHandler(   [ '-r', '--repo' ],    'repo_path'  ) )
ScriptOpts.addHandler( cmdopts.EnvFlagSet(      [ '-v', '--verbose' ], 'verbose'    ) )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# handler functions for commands

def cmdHelp( argv, env ):
   'show usage and syntax'
   assert argv[0] == 'help'
   showUsage()
ScriptCmds.add( cmdopts.Command( 'help', cmdHelp ) )

def cmdDump( argv, env ):
   'dump the environment'
   assert argv[0] == 'dump'
   print 'opts:\t%s' % ( Options )
   print 'args:\t%s' % ( Args )
   print 'script env:'
   print '   %s' % ScriptEnv
   GlobalEnv.dump()
   ScriptOpts.dump()
ScriptCmds.add( cmdopts.Command( 'dump', cmdDump ) )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# main

# step 1 - parse the script arguments

try:
   Options, Args = ScriptOpts.parseArgs( sys.argv[1:] )
except getopt.GetoptError, err:
   barf( str(err) )
   sys.exit(2)

for opt, param in Options:
   ScriptOpts.execute( opt, param, GlobalEnv )

# step 2- if no command is specified, set the default

if 0 == len(Args):
   Args = ScriptDefaultArgs


# step 3 - dispatch the command

if ScriptCmds.isSupported( Args[0] ):

   ScriptCmds.execute( Args, GlobalEnv )

else:

   GitCmds = git.getCommands()

   if GitCmds.isSupported( Args[0] ):

      try:
         GitCmds.execute( Args, GlobalEnv )
      except getopt.GetoptError, err:
         barf( str(err) )
         sys.exit(2)

   else:
      barf( '''command '%s' not recognized''' % ( Args[0] ) )


# vim: si
