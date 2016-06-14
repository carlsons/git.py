#! /usr/bin/python

'''sample script for implementing the status command'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing svn.commands.status module"

import scm
import svn

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

command_name = 'status'

class StatusCommand( scm.Command ):

   def __init__( self ):
      super( StatusCommand, self ).__init__( command_name )

   def get_command_parser( self, parent_parser ):

      parser = super( StatusCommand, self ).get_command_parser( parent_parser )

      parser.add_argument(
         '-s', '--short',
         help              =  'show short status',
         default           =  None,
         action            =  'store_const', const=True
         )

      return parser

   def process( self, parent_parsers, args ):
      # print "processing the svn %s command..." % ( self.command_name )

      super( StatusCommand, self ).process( parent_parsers, args )

      print 'args  = ' + repr( self.args )
      print "processing the svn '%s' command for repo '%s'" % ( self.command_name, args.root )

      pass

   def show_help( self, parent_parsers, args ):
      # print "help for the svn %s command..." % ( self.command_name )

      parser = self.get_command_parser( parent_parsers[ 'root' ] )
      ignore = parser.parse_args( [ '-h' ] )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

svn.register_command( command_name, StatusCommand() )

