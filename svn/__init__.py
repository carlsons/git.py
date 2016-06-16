#! /usr/bin/python

'''Subversion package'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing svn package"

_Type                = 'svn'
_MetaDir             = '.svn'

import scm

from common import *

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

supported_cmdlist = {}

def register_command( command_name, handler ):
   global supported_cmdlist
   supported_cmdlist[ command_name ] = handler

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# functions for finding and testing the existence of a Subversion repo

def is_repo( path=None ):
   path = munge_dir( path )
   if has_dir( path, _MetaDir ):
      return not has_dir( get_parent_dir( path ), _MetaDir )
   return False

def find_repo_root( path=None ):
   return find_dir( path, is_repo, None );

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# TODO: need a derived class for this scm

def find_repo( path=None ):
   root = find_repo_root( path )
   if root:
      return scm.Repo( _Type, root )
   return None

