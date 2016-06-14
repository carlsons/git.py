#! /usr/bin/python

'''common package, generic stuff used by everyone'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

import os
import exceptions

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def getParentDir( path ):
   parent_dir, ignore = os.path.split( path )
   return parent_dir

def checkDirExists( path ):
   if not os.path.isdir( path ):
      raise exceptions.RuntimeError, "not a directory: " + repr(path)

def hasDir( path, dirname ):
   target = os.path.join( path, dirname )
   return os.path.isdir( target )

def mungeDir( path=None ):
   # if a path is not specified, use the current dir
   if path is None:
      path = os.getcwd()
   # expand the user directory
   path = os.path.expanduser( path )
   # finally, verify that the path exists
   checkDirExists( path )
   # get the real path
   path = os.path.realpath( path )
   # and return it
   return path

def findDir( path, func, arg ):
   path = mungeDir( path )
   while True:
      if func( path ):     # is this the path we're looking for?
         return path
      if path == '/':      # stop if you reach the root
         return None
      path, d = os.path.split( path )

# child wins 
def merge_dict( parent, child ):

   merged = {}
   for k in set( parent.keys() + child.keys() ):
      if child.get( k, None ) is None:
         merged[ k ] = parent.get( k, None )
      else:
         merged[ k ] = child.get( k )

   return merged

