#! /usr/bin/python

'''sample script for implementing the help command'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing git.commands.help module"

import git

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

command_name = 'help'

class HelpCommand( git.Command ):

   def __init__( self ):
      super( HelpCommand, self ).__init__( command_name )

   def process( self, args ):

      print "processing the git %s command..." % ( self.command_name )
      print args

      if len( args.options ) == 0:
         raise exceptions.RuntimeError, "command not specified"

      elif not git.supported_cmdlist.has_key( args.options[0] ):
         raise exceptions.RuntimeError, "command not supported: " + args.options[0]

      else:
         git.supported_cmdlist[ args.options[0] ].show_help( args )

   def show_help( self, args ):
      print "help for the git %s command..." % ( self.command_name )
      print args

git.register_command( 'help', HelpCommand() )

