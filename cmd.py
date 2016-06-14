#! /usr/bin/python

import os
import sys

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def dumpit( varname ):
   cmd = "_val = repr(%s)" % ( varname )
   exec cmd
   print "%20s = %s" % ( varname, _val )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

dumpit( '__name__' )
dumpit( 'sys.argv' )

orig_path, orig_base = os.path.split( sys.argv[0] )

dumpit( 'orig_base' )

script = os.path.realpath( sys.argv[0] )

dumpit( 'script' )

script_path, script_base = os.path.split( script )

dumpit( 'script_path' )
dumpit( 'script_base' )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

import svn

print svn.findRepo( '/home/carlsons/sandbox/svn-mirror/work/conf' )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

import git

print git.findRepo( '/home/carlsons/sandbox/git.py/git/commands' )


