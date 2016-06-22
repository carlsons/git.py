#! /usr/bin/python

'''scm package'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# print "importing scm package"

import os
import argparse

# TODO: do we want to import into this namespace?
from common import *

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# TODO: do these belong here?

script_description = 'SCM wrapper script'

script_version     = '1.0-2016.05.27-01'

usage_epilog       = '''

For help on a specific command, use the help command, e.g.:

   %(prog)s help <command>

'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# TODO: do we need this construct?

def show_example( cmdline_parser, args ):
   print "TODO: fill me in!"

global_cmdlist={
 'example' : show_example
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def get_root_parser():

   root_parser = argparse.ArgumentParser(
      description       = script_description,
      epilog            = usage_epilog,
      formatter_class   = argparse.RawDescriptionHelpFormatter,
      add_help          = False
      )

   root_parser.add_argument(
      '--version',
      action            =  'version',
      version           =  '%(prog)s: ' + script_description + ', version ' + script_version
      )

   root_parser.add_argument(
      '-v', '--verbose',
      help              =  'enable verbose mode',
      default           =  None,
      action            =  'store_const', const=True
      )

   root_parser.add_argument(
      '--debug',
      help              =  'enable debug mode',
      default           =  None,
      action            =  'store_const', const=True
      )

   root_parser.add_argument(
      '--root',
      help              =  'specify the root directory of the repository',
      default           =  None,
      action            =  'store'
      )

   return root_parser

def get_global_parser( root_parser ):

   global_parser = argparse.ArgumentParser(
      formatter_class   = argparse.RawDescriptionHelpFormatter,
      parents           = [ root_parser ],
      add_help          = False
      )

   global_parser.add_argument(
      '-h', '--help',
      help              =  'show help (placeholder)',
      default           =  None,
      action            =  'store_const', const=True
      )

   global_parser.add_argument(
      'options',
      help              =  'command specfic options',
      nargs             =  argparse.REMAINDER
      )

   return global_parser

def get_cmdline_parser( root_parser, supported_cmdlist ):

   cmdline_parser = argparse.ArgumentParser(
      formatter_class   = argparse.RawDescriptionHelpFormatter,
      parents           = [ root_parser ],
      add_help          = True
      )

   cmdline_parser.add_argument(
      'command',
      help              =  'command to execute',
      nargs             =  '?',
      choices           =  global_cmdlist.keys() + supported_cmdlist.keys(),
      default           =  None,
      action            =  'store'
      )

   cmdline_parser.add_argument(
      'options',
      help              =  'command specfic options',
      nargs             =  argparse.REMAINDER
      )

   return cmdline_parser

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class Command( object ):

   def __init__( self, command_name ):
      self.command_name = command_name

   def get_command_parser( self, parent_parser ):

      parser = argparse.ArgumentParser(
         description       = script_description,
         formatter_class   = argparse.RawDescriptionHelpFormatter,
         parents           = [ parent_parser ],
         add_help          = True
         )

      parser.add_argument(
         'command',
         help              =  'command to execute',
         nargs             =  '?',
         choices           =  [ self.command_name ],
         default           =  None,
         action            =  'store'
         )

      return parser

   def process( self, parent_parsers, args ):
      assert args.command == self.command_name

      parser      = self.get_command_parser( parent_parsers[ 'global' ] )
      my_args     = parser.parse_args( args.options )
      self.args   = merge_dict( args.__dict__, my_args.__dict__ )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class Scm( object ):

   def __init__( self, name, scm_type, scm_dirname ):
      self.name            = name
      self.scm_type        = scm_type
      self.scm_dirname     = scm_dirname
      self.commands        = {}

   def register_command( self, command_name, handler ):
      assert not self.commands.has_key( command_name )
      self.commands[ command_name ] = handler

   def find_repo_root( self, path ):
      return find_dir( path, self.is_repo, None );

   def find_repo( self, path=None ):
      munged_path = Path( path )
      root = self.find_repo_root( str( munged_path ) )
      if root:
         return Repo( self, Path(root) )
      return None

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class Repo:

   def __init__( self, scm_obj, path ):
      check_dir_exists( str( path ) )
      # set the data members
      self.scm_obj         = scm_obj
      self.path            = path
      self.cwd             = os.getcwd()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

import git
import svn

def find_repos( path=None ):

   g = git.scm_obj.find_repo( path )
   s = svn.scm_obj.find_repo( path )

   r = { 'git' : g, 'svn' : s }

   f = []

   t = None

   if    not g and not s:

      pass

   elif      g and not s:

      t = 'git'
      f.append( g )

   elif  not g and     s:

      t = 'svn'
      f.append( s )

   else:

      t = 'both'
      f.extend([  g, s ] )

   r[ 'type'  ] = t
   r[ 'found' ] = f

   return r

