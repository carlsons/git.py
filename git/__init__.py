#! /usr/bin/python

'''git package'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing git package"

import os

import argparse

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# TODO: do these belong here?

script_description = 'Git wrapper script'

script_version     = '1.0-2016.05.27-01'

usage_epilog       = '''

For help on a specific command, use the help command, e.g.:

   %(prog)s help <command>

'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

supported_cmdlist = {}

def register_command( command_name, handler ):
   supported_cmdlist[ command_name ] = handler

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# TODO: do we need this construct?

def show_example( cmdline_parser, args ):
   print "TODO: fill me in!"

global_cmdlist={
 'example' : show_example
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def get_parsers():

   global_parser = argparse.ArgumentParser(
      description       = script_description,
      epilog            = usage_epilog,
      formatter_class   = argparse.RawDescriptionHelpFormatter,
      add_help          = False
      )

   global_parser.add_argument(
      '--version',
      action            =  'version',
      version           =  '%(prog)s: ' + script_description + ', version ' + script_version
      )

   global_parser.add_argument(
      '-v', '--verbose',
      help              =  'enable verbose mode',
      default           =  False,
      action            =  'store_const', const=True
      )

   global_parser.add_argument(
      '--debug',
      help              =  'enable debug mode',
      default           =  False,
      action            =  'store_const', const=True
      )

   global_parser.add_argument(
      '--root',
      help              =  'specify the root directory of the Git repository',
      default           =  os.getcwd(),
      action            =  'store'
      )

   cmdline_parser = argparse.ArgumentParser(
      formatter_class   = argparse.RawDescriptionHelpFormatter,
      parents           = [ global_parser ],
      )

   cmdline_parser.add_argument(
      'command',
      help              =  'command to execute',
      nargs             =  '?',
      choices           =  global_cmdlist.keys() + supported_cmdlist.keys(),
      default           =  'status',
      action            =  'store'
      )

   cmdline_parser.add_argument(
      'options',
      help              =  'command specfic options',
      nargs             =  argparse.REMAINDER
      )

   return ( { 'global' : global_parser, 'cmdline' : cmdline_parser } )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class Command( object ):

   def __init__( self, command_name ):
      self.command_name = command_name

   def get_command_parser( self, parent_parser ):

      parser = argparse.ArgumentParser(
         description       = script_description,
         formatter_class   = argparse.RawDescriptionHelpFormatter,
         parents           = [ parent_parser ]
         )

      parser.add_argument(
         'command',
         help              =  'command to execute',
         nargs             =  '?',
         choices           =  [ self.command_name ],
         default           =  'status',
         action            =  'store'
         )

      return parser

