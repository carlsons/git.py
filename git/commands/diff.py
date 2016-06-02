#! /usr/bin/python

'''sample script for implementing the diff command'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing git.commands.diff module"

import git

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

command_name = 'diff'

class DiffCommand( git.Command ):

   def __init__( self ):
      super( DiffCommand, self ).__init__( command_name )

   def process( self, args ):
      print "processing the git %s command..." % ( self.command_name )
      print args

   def show_help( self, args ):
      print "help for the git %s command..." % ( self.command_name )
      print args

git.register_command( 'diff', DiffCommand() )

