#! /usr/bin/python

''' this module implements a mechanism for defining a data-driven command line interface '''

import os.path
import getopt
import copy

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class Environ:
   def __init__( self, name ):
      self.name      = name
      self.lookup    = {}
      self.parent    = None

   def setParent( self, parent ):
      self.parent    = parent

   def add( self, obj ):
      assert not self.lookup.has_key( obj.name )
      self.lookup[ obj.name ] = obj

   def set( self, name, value=None ):
      if self.lookup.has_key( name ):
         self.lookup[ name ].set( value )
      elif not self.parent is None:
         self.parent.set( name, value )
      else:
         raise exceptions.RuntimeError, "variable not known: " + name

   def has_var( self, name ):
      return self.lookup.has_key( name )

   def get( self, name ):

      # if there's no parent or the parent doesn't have the var
      if self.parent is None or not self.parent.has_var( name ):
         if not self.has_var( name ):
            raise exceptions.RuntimeError, "variable not known: " + name
         return self.lookup[ name ].get()

      # if only the parent has the var
      if not self.has_var( name ):
         return self.parent.lookup[ name ].get()

      parent_var = self.parent.lookup[ name ]
      local_var  = self.lookup[ name ]

      # if the local value is set
      if not local_var.value is None:
         return local_var.value

      if not parent_var.value is None:
         return parent_var.value

      if not local_var.default is None:
         return local_var.default

      return parent_var.default


   def dump( self ):
      print "%s environment:" % self.name
      for k in self.lookup:
         self.lookup[k].dump()

class EnvFlag:
   def __init__( self, name ):
      self.name      = name
      self.value     = None
      self.default   = False

   def set( self, *args ):
      self.value     = True

   def get( self ):
      return self.value == True

   def dump( self ):
      print '   %s:\tval=%s' % ( self.name, repr(self.value) )

class EnvVar:
   def __init__( self, name, data_type=None, default=None, value=None, constant=False ):
      self.name      = name
      self.data_type = data_type
      self.default   = default
      self.value     = value
      self.constant  = constant
      if constant:
         assert not value is None

   def set( self, value ):
      if self.data_type is None:
         self.value  = value
      else:
         self.data_type( self, value )

   def get( self ):
      if self.value is None:  # value not set
         return self.default  # return the default
      else:
         return self.value    # else return the value

   def dump( self ):
      print '   %s:\tval=%s\tdef=%s' % ( self.name, repr(self.value), self.default )


def varBOOL( var, value ):
   var.value         = value == True

def varPATH( var, path ):
   if not os.path.isdir( path ):
      raise exceptions.RuntimeError, "not a directory: " + repr(path)
   var.value         = path


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class Options:
   def __init__( self ):
      self.short_opts   = []
      self.long_opts    = []
      self.lookup       = {}

   def addHandler( self, handler ):
      for opt in handler.opts:
         opt_stripped = opt.lstrip( '-' );
         if opt[1] == '-':
            assert not self.lookup.has_key( opt )
            self.lookup[ opt ] = handler
            if handler.needsParam():
               opt_stripped += '='
            self.long_opts.append( opt_stripped )
         else:
            for c in opt_stripped:
               opt = '-'+c
               assert not self.lookup.has_key( opt )
               self.lookup[ opt ] = handler
               if handler.needsParam():
                  c += ':'
               self.short_opts.append( c )

   def parseArgs( self, argv ):
      opts, argv  = getopt.getopt( argv, ''.join(self.short_opts), self.long_opts )
      return opts, argv

   def execute( self, opt, param, env ):
      handler = self.lookup[ opt ]
      handler.execute( param, env )

   def dump( self ):
      print 'script options:'
      for k in self.lookup:
         print '   %s option:' % ( k )
         self.lookup[k].dump()


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class EnvFlagSet:
   def __init__( self, opts, opt_name ):
      self.opts         = opts
      self.opt_name     = opt_name
   def needsParam( self ):
      return False
   def execute( self, param, env ):
      env.set( self.opt_name )
   def dump( self ):
      print '      %24s: %20s ->\topts=%s' % ( self.__class__, self.opt_name, repr(self.opts) )

class EnvVarHandler:
   def __init__( self, opts, opt_name ):
      self.opts         = opts
      self.opt_name     = opt_name
   def needsParam( self ):
      return True
   def execute( self, param, env ):
      env.set( self.opt_name, param )
   def dump( self ):
      print '      %24s: %20s ->\topts=%s' % ( self.__class__, self.opt_name, repr(self.opts) )

class OptHandler:
   def __init__( self, opts, func ):
      self.opts         = opts
      self.func         = func
   def needsParam( self ):
      return False
   def execute( self, param, env ):
      self.func( env )
   def dump( self ):
      print '      %24s: %20s ->\tfunc=%s' % ( self.__class__, repr(self.opts), repr(self.func) )

class ParmHandler:
   def __init__( self, opts, func ):
      self.opts         = opts
      self.func         = func
   def needsParam( self ):
      return True
   def execute( self, param, env ):
      self.func( param, env )
   def dump( self ):
      print '      %24s: %20s ->\tfunc=%s' % ( self.__class__, repr(self.opts), repr(self.func) )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# common option handlers

def optVerbose( env ):
   'show more detail'
   env.set( 'verbose' )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class Commands:
   def __init__( self ):
      self.lookup       = {}

   def add( self, command ):
      assert not self.lookup.has_key( command.name )
      self.lookup[ command.name ] = command

   def isSupported( self, name ):
      return self.lookup.has_key( name )

   def execute( self, argv, env ):
      assert 0 < len(argv)
      name = argv[0]
      if self.isSupported( name ):
         command = self.lookup[ name ]
         command.execute( argv, env )
      else:
         raise exceptions.RuntimeError, "unknown command: " + name

class Command:
   def __init__( self, name, func, env_template=None, opts=None ):
      self.lookup       = {}
      self.name         = name
      self.func         = func
      self.env_template = env_template
      self.opt_template = opts

   def execute( self, argv, global_env ):
      assert 0 < len(argv)

      # construct the local environment
      if self.env_template is None:
         # none was given, so make an empty one
         local_env = Environ( 'self.name' )
      else:
         # otherwise, clone the template
         local_env = copy.deepcopy( self.env_template );
      # and then set the parent
      local_env.setParent( global_env );

      # execute the options
      if not self.opt_template is None:
         # parse the options
         try:
            options, args = self.opt_template.parseArgs( argv[1:] )
         except getopt.GetoptError, err:
            # print help information and exit:
            raise getopt.GetoptError, '%s: %s' % ( self.name, str(err) )
         # and then execute them
         for opt, param in options:
            self.opt_template.execute( opt, param, local_env )

      # then finally, execute the command
      self.func( argv, local_env )

# vim: si
