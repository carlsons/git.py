#! /usr/bin/python

'''common package, generic stuff used by everyone'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

import os
import exceptions

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# os directory functions

def get_parent_dir( path ):
   'get the parent directory of the given path'
   parent_dir, ignore = os.path.split( path )
   return parent_dir

def check_dir_exists( path ):
   'check to see if the given path exists, raise an exception if not'
   if not path:
      raise exceptions.RuntimeError, "no directory specified: " + repr(path)
   elif not os.path.isdir( path ):
      raise exceptions.RuntimeError, "not a directory: " + repr(path)

def has_dir( path, dirname ):
   'check to see if the given dirname exists in the given path'
   target = os.path.join( path, dirname )
   return os.path.isdir( target )

def find_dir( path, func, arg ):
   '''enumerate all of the directories in given path, calling the given func
for each until it returns true or it reaches the root'''
   while True:
      if func( path ):     # is this the path we're looking for?
         return path
      if path == '/':      # stop if you reach the root
         return None
      path, d = os.path.split( path )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# dictionary functions

# child wins 
def merge_dict( parent, child ):
   '''merge the key/value pairs in parent and child where an entry in the child
takes precedence over the corresponding entry in the parent'''

   merged = {}
   for k in set( parent.keys() + child.keys() ):
      if child.get( k, None ) is None:
         merged[ k ] = parent.get( k, None )
      else:
         merged[ k ] = child.get( k )

   return merged

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def munge( path=None ):
   'munge the given path, i.e.: cannonicalize it to a real path'
   # if a path is not specified, use the current dir
   if path is None:
      path = os.getcwd()
   # expand the user directory
   path = os.path.expanduser( path )
   # finally, verify that the path exists
   check_dir_exists( path )
   # get the real path
   path = os.path.realpath( path )
   # and return it
   return path

class Path( object ):

   def __init__( self, orig_path = None ):
      self.orig_path = orig_path
      self.path      = munge( orig_path )

   def __str__( self ):
      return self.path

   def get( self ):
      return self.path

   def get_orig( self ):
      return self.orig_path

   def goto_parent( self ):
      '''change the path the parent directory of the current path'''
      self.path, ignore = os.path.split( self.path )

   def has_dir( self, dirname ):
      '''check to see if the given dirname exists in the current path'''
      spec = os.path.join( self.path, dirname )
      return os.path.isdir( spec )

   def parent_has_dir( self, dirname ):
      '''check to see if the given dirname exists in the parent of the current path'''
      parent_dir, ignore = os.path.split( self.path )
      spec = os.path.join( parent_dir, dirname )
      return os.path.isdir( spec )

   def find_dir( self, func ):
      '''enumerate all of the directories in this path, calling the given func
         for each until it returns true or it reaches the root'''
      while True:
         if func( self ):        # is this the path we're looking for?
            return True
         if self.path == '/':    # stop if you reach the root
            return False
         self.goto_parent()
