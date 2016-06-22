#! /usr/bin/python

if True:

   import os
   import sys

   # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

   def dumpit( varname ):
      cmd = "_val = repr(%s)" % ( varname )
      exec cmd
      print "%20s =  %s" % ( varname, _val )

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

   dirs = [ '/home/carlsons/sandbox/svn-mirror/work/conf', '/home/carlsons/sandbox/git.py/git/commands', '/home/carlsons/projects/work' ]

   import scm

   for dir_ in dirs:

      print "\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-="
      print "directory: %s\n" % ( dir_ )

      repos = scm.find_repos( dir_ )

      print "repos:"
      for k,v in sorted( repos.items() ):
         print "%20s -> %s (%s)" % (k,v,type(v))

      if repos[ 'found' ]:
         print "found:"
         for r in repos[ 'found' ]:
            for k,v in sorted( r.__dict__.items() ):
               print "%20s -> %s (%s)" % (k,v,type(v))
      else:
         print "no repos found"

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if False:

   def f( path ):
      print path
      return path.parent_has_dir( '.git' )

   import common

   p = common.Path()

   p.find_dir( f )

   assert isinstance( p, common.Path )
