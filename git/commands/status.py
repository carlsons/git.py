#! /usr/bin/python

'''sample script for implementing the status command'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing git.commands.status module"

import git

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

command_name = 'status'

class StatusCommand( git.Command ):

   def __init__( self ):
      super( StatusCommand, self ).__init__( command_name )

   def process( self, args ):
      print "processing the git %s command..." % ( self.command_name )
      print args

   def show_help( self, args ):
      print "help for the git %s command..." % ( self.command_name )
      print args

git.register_command( 'status', StatusCommand() )

