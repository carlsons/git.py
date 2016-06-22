#! /usr/bin/python

'''Subversion package'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing svn package"

_NAME                = 'Subversion'
_SCM_TYPE            = 'svn'
_SCM_DIRNAME         = '.svn'

import scm

from common import *

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class SvnScm( scm.Scm ):

   def __init__( self ):
      super( SvnScm, self ).__init__( _NAME, _SCM_TYPE, _SCM_DIRNAME )

   def is_repo( self, path ):
      if path.has_dir( self.scm_dirname ):
         return not path.parent_has_dir( self.scm_dirname )
      return False

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

scm_obj = SvnScm()

