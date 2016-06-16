#! /usr/bin/python

'''Git package'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing git package"

_Type                = 'git'
_MetaDir             = '.git'

import scm

from common import *

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

supported_cmdlist = {}

def register_command( command_name, handler ):
   global supported_cmdlist
   supported_cmdlist[ command_name ] = handler

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# functions for finding and testing the existence of a Git repo

def is_repo( path=None ):
   path = munge_dir( path )
   return has_dir( path, _MetaDir )

def find_repo_root( path=None ):
   return find_dir( path, is_repo, None );

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# TODO: need a derived class for this scm

def find_repo( path=None ):
   root = find_repo_root( path )
   if root:
      return scm.Repo( _Type, root )
   return None

