
if __name__ == '__main__':
   import sys
   if len( sys.argv ) > 1:
      print isrepo( sys.argv[1] )
   else:
      print isrepo()


LocalEnv = Environ( 'Local' )
LocalEnv.setParent( GlobalEnv )

LocalEnv.add( EnvVar(  'repo_path', varPATH ) )

print '-------------------------'

GlobalEnv.dump()
LocalEnv.dump()

print 'DEBUG: repo_path =', LocalEnv.get( 'repo_path' )
print 'DEBUG: verbose   =', LocalEnv.get( 'verbose' )

print '-------------------------'

LocalEnv.set( 'repo_path', '/home/carlsons/sandbox/git' )
LocalEnv.set( 'verbose' )

GlobalEnv.dump()
LocalEnv.dump()

print 'DEBUG: repo_path =', LocalEnv.get( 'repo_path' )
print 'DEBUG: verbose   =', LocalEnv.get( 'verbose' )

print '-------------------------'
