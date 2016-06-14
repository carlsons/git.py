#! /usr/bin/python

'''sample script for implementing the diff command'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing svn.commands.diff module"

import scm
import svn

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

command_name = 'diff'

class DiffCommand( scm.Command ):

   def __init__( self ):
      super( DiffCommand, self ).__init__( command_name )

   def get_command_parser( self, parent_parser ):

      parser = super( DiffCommand, self ).get_command_parser( parent_parser )

      parser.add_argument(
         '-w',
         help              =  'ignore whitespace',
         default           =  False,
         action            =  'store_const', const=True
         )

      return parser

   def process( self, parent_parsers, args ):
      # print "processing the svn %s command..." % ( self.command_name )

      pass

   def show_help( self, parent_parsers, args ):
      # print "help for the svn %s command..." % ( self.command_name )

      parser = self.get_command_parser( parent_parsers[ 'root' ] )
      ignore = parser.parse_args( [ '-h' ] )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

svn.register_command( command_name, DiffCommand() )

