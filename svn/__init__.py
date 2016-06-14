#! /usr/bin/python

'''Subversion package'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing svn package"

_MetaDir             = '.svn'

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

supported_cmdlist = {}

def register_command( command_name, handler ):
   global supported_cmdlist
   supported_cmdlist[ command_name ] = handler

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# functions for finding and testing the existence of a Subversion repo

def isRepo( path=None ):
   path = mungeDir( path )
   if hasDir( path, _MetaDir ):
      return not hasDir( getParentDir( path ), _MetaDir )
   return False

def findRepo( path=None ):
   return findDir( path, isRepo, None );

