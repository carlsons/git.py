#! /usr/bin/python

'''sample ui script'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

script_description = 'Git wrapper script'
script_version     = '1.0-2016.05.27-01'

usage_epilog       = '''

For help on a specific command, use the help command, e.g.:

   %(prog)s help <command>

'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def show_example( args ):
   print "TODO: fill me in!"


global_cmdlist={
 'example' : show_example
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

import os
import exceptions
import pprint

import git.commands

import argparse
cmdline_parser = argparse.ArgumentParser(
   description       = script_description,
   epilog            = usage_epilog,
   formatter_class   = argparse.RawDescriptionHelpFormatter
   )

cmdline_parser.add_argument(
   '--version',
   action            =  'version',
   version           =  '%(prog)s: ' + script_description + ', version ' + script_version
   )

cmdline_parser.add_argument(
   '-v', '--verbose',
   help              =  'enable verbose mode',
   default           =  False,
   action            =  'store_const', const=True
   )

cmdline_parser.add_argument(
   '--debug',
   help              =  'enable debug mode',
   default           =  False,
   action            =  'store_const', const=True
   )

cmdline_parser.add_argument(
   '--root',
   help              =  'specify the root directory of the Git repository',
   default           =  os.getcwd(),
   action            =  'store'
   )


cmdline_parser.add_argument(
   'command',
   help              =  'command to execute',
   nargs             =  '?',
   choices           =  global_cmdlist.keys() + git.supported_cmdlist.keys(),
   default           =  'status',
   action            =  'store'
   )

cmdline_parser.add_argument(
   'options',
   help              =  'command specfic options',
   nargs             =  argparse.REMAINDER
   )


args = cmdline_parser.parse_args()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if args.debug:
   print 'command line arguments: '
   pprint.pprint( args.__dict__, indent=3 )
   print 'supported commands: '
   pprint.pprint( git.supported_cmdlist, indent=3 )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if    global_cmdlist.has_key( args.command ):

   global_cmdlist[ args.command ]( args )

elif  git.supported_cmdlist.has_key( args.command ):

   git.supported_cmdlist[ args.command ].process( args)

else:

   raise exceptions.RuntimeError, "command not supported: " + repr(args.command)

