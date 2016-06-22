#! /usr/bin/python

'''Git package'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing git package"

_NAME                = 'Git'
_SCM_TYPE            = 'git'
_SCM_DIRNAME         = '.git'

import scm

from common import *

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class GitScm( scm.Scm ):

   def __init__( self ):
      super( GitScm, self ).__init__( _NAME, _SCM_TYPE, _SCM_DIRNAME )

   def is_repo( self, path ):
      return path.has_dir( self.scm_dirname )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

scm_obj = GitScm()

