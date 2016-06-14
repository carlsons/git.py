#! /usr/bin/python

'''sample script for implementing the help command'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing svn.commands.help module"

import exceptions

import scm
import svn

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

command_name = 'help'

class HelpCommand( scm.Command ):

   def __init__( self ):
      super( HelpCommand, self ).__init__( command_name )

   def process( self, parent_parsers, args ):
      # print "processing the svn %s command..." % ( self.command_name )

      if len( args.options ) == 0:
         ignore = parent_parsers[ 'cmdline' ].parse_args( [ '-h' ] )

      elif not svn.supported_cmdlist.has_key( args.options[0] ):
         raise exceptions.RuntimeError, "command not supported: " + args.options[0]

      else:
         svn.supported_cmdlist[ args.options[0] ].show_help( parent_parsers, args )

   def show_help( self, parent_parsers, args ):
      # print "help for the svn %s command..." % ( self.command_name )

      pass

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

svn.register_command( command_name, HelpCommand() )
import scm

