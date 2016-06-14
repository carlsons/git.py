#! /usr/bin/python

'''Git package'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing git package"

_MetaDir             = '.git'

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

supported_cmdlist = {}

def register_command( command_name, handler ):
   global supported_cmdlist
   supported_cmdlist[ command_name ] = handler

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# functions for finding and testing the existence of a Git repo

def isRepo( path=None ):
   path = mungeDir( path )
   return hasDir( path, _MetaDir )

def findRepo( path=None ):
   return findDir( path, isRepo, None );

