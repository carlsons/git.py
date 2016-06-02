#! /usr/bin/python

'''git package'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing git package"

class Command( object ):

   def __init__( self, command_name ):
      self.command_name = command_name

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

supported_cmdlist = {}

def register_command( command_name, handler ):
   supported_cmdlist[ command_name ] = handler


