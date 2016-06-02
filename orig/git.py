#! /usr/bin/python

''' this module implements the Git-specific commands for the Python-based Git wrapper '''

import os
import os.path
import exceptions
import subprocess
import getopt

from colorize import *
from git_include import *

import cmdopts


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# local environment

Colorize             = True # TODO: this needs to come from the ScriptEnv

_MetaDir             = '.git'
_DescriptionFile     = 'description'

_Exe                 = [ 'git' ]
_GitStatus           = [ 'status', '--porcelain', '--ignored', '--untracked=all' ]
_GitBranches         = [ 'branch' ]

_SplitEntry          = ( 'R' )

_Groups              = [ 'commit', 'unmerged', 'modified', 'untracked', 'ignored' ]
_GroupDefs           = { }

def addGroupDef( group ):
   global _GroupDefs
   _GroupDefs[ group.name ] = group

class GroupDef:
   def __init__( self, name, required=True, clean=True, summary=( YELLOW, BLACK, True ) ):
      self.name      = name
      self.required  = required  # required section, always shown
      self.clean     = clean     # show group if CLEAN
      self.summary   = summary   # fg color for group summary


addGroupDef( GroupDef( 'commit',   summary=( RED, BLACK, True ) ) )
addGroupDef( GroupDef( 'unmerged', clean=False                   ) )
addGroupDef( GroupDef( 'modified'                                ) )
addGroupDef( GroupDef( 'untracked'                               ) )
addGroupDef( GroupDef( 'ignored',  required=False, clean=False   ) )

_Unmodified          = ' '
_Modified            = 'M'

_ModifiedInIndex     = ( 'M', 'A', 'D', 'R', 'C' )

_StatusGroups        = ( '?', '!' ) # status descriptors that map directly to groups

_StatusDescriptors   = {
   ' ' : 'unmodified',
   'M' : 'modified',
   'A' : 'added',
   'D' : 'deleted',
   'R' : 'renamed',
   'C' : 'copied',
   'U' : 'updated',
   '?' : 'untracked',
   '!' : 'ignored'
}

_UnmergedDescriptors = {
   ( 'D', 'D' ) : "unmerged, both deleted",
   ( 'A', 'U' ) : "unmerged, added by us",
   ( 'U', 'D' ) : "unmerged, deleted by them",
   ( 'U', 'A' ) : "unmerged, added by them",
   ( 'D', 'U' ) : "unmerged, deleted by us",
   ( 'A', 'A' ) : "unmerged, both added",
   ( 'U', 'U' ) : "unmerged, both modified"
}

_CLEAN = 'CLEAN'

TXT_INFO, TXT_NOTICE, TXT_WARNING, TXT_ERROR, TXT_CRITICAL = range(5)
TXT_COLORS = [ 
   ( WHITE,    BLACK, False ),   # TXT_INFO     just a placeholder, ignored by colorize comments
   ( YELLOW,   BLACK, False ),   # TXT_NOTICE
   ( MAGENTA,  BLACK, True  ),   # TXT_WARNING
   ( RED,      BLACK, True  ),   # TXT_ERROR
   ( WHITE,    RED,   True  )    # TXT_CRITICAL
]

def colorizeComments( comments ):
   str_list = [ colorize( comment, *TXT_COLORS[level] ) for comment, level in comments ]
   return ','.join( str_list )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def showAnnotated( prompt, text ):
   print "%4s: %s" % ( prompt, text )

def showHeading( heading ):
   print "%s:" % ( heading.capitalize() )

def showText( text ):
   print "   %s" % text

def getText_CLEAN():
   if Colorize:
      return colorize( _CLEAN, fg=GREEN, bold=True )
   else:
      return  _CLEAN

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# functions for finding and testing the existence of a Git repo

def shortenPath( path ):
   Home = os.environ['HOME'] + '/'
   if path[0:len(Home)] == Home:
      return "~/%s" % path[len(Home):]
   return path

def checkDir( path ):
   if not os.path.isdir( path ):
      raise exceptions.RuntimeError, "not a directory: " + repr(path)

def walkPath( path, func, arg ):
   checkDir( path )
   path = os.path.abspath( path )
   while True:
      if func( path ):     # is this the path we're looking for?
         return path
      if path == '/':      # stop if you reach the root
         return None
      path, d = os.path.split( path )

def isRepo( path=None ):
   if path is None:
      path = '.'
   checkDir( path )
   spec = os.path.join( path, _MetaDir )
   if os.path.isdir( spec ):
      return True
   return False

def findRepo( path=None ):
   if path is None:
      path = os.getcwd()
   return walkPath( path, isRepo, None );

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def check_output( cmd, path=None ):
   if path:
      checkDir( path )
      cwd = os.getcwd()
      os.chdir( path )
   data = subprocess.check_output( _Exe + cmd )
   if path:
      os.chdir( cwd )
   return data

def check_call( cmd, path=None ):
   if path:
      checkDir( path )
      cwd = os.getcwd()
      os.chdir( path )
   subprocess.check_call( _Exe + cmd )
   if path:
      os.chdir( cwd )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class File:
   def __init__( self, raw_entry ):
      # get the status descriptors
      index = raw_entry[0]
      local = raw_entry[1]
      assert _StatusDescriptors.has_key( local )
      assert _StatusDescriptors.has_key( index )
      # start intializing data members
      self.status          = ( index, local )
      if index in _SplitEntry or local in _SplitEntry:
         files             =  raw_entry[3:].split( ' -> ' )
         self.name         = files[0]
         self.new_name     = files[1]
      else:
         self.name         = raw_entry[3:]
         self.new_name     = None

      # decode the status, determine in which groups this file entry belongs
      # and add group entries for each
      self.groups          = []

      # pick out statuses that map directly to groups
      if    index in _StatusGroups:
         self.groups.append( ( self, _StatusDescriptors[index], [] ) )
      # look for the combos that map to unmerged
      elif  _UnmergedDescriptors.has_key( self.status ):
         self.groups.append( ( self, 'unmerged', _UnmergedDescriptors[ self.status ] ) )
      # map into commit and modified groups
      else:
         # find items that belong in the commit group
         if not index == _Unmodified:
            comments = []
            if not index == _Modified:
               comments.append( ( _StatusDescriptors[ index ], TXT_INFO ) )
            if not local == _Unmodified:
               comment_str = "%s locally" % ( _StatusDescriptors[ local ] )
               comments.append( ( comment_str, TXT_NOTICE ) )
            self.groups.append( ( self, 'commit', comments ) )

         # find items that belong in the modified group
         if not local == _Unmodified:
            comments = []
            if not local == _Modified:
               comments.append( ( _StatusDescriptors[ local ], TXT_INFO ) )
            self.groups.append( ( self, 'modified', comments ) )

      if not len( self.groups ):
         raise exceptions.RuntimeError, "unexpected entry status: " + repr( self.status )

   def getDescriptor( self ):
      if self.new_name is None:
         return self.name
      return "%s -> %s" % ( self.name, self.new_name )

   def dump( self ):
      index, local         = self.status
      if self.new_name is None:
         showText( "%s%s %s"        % ( index, local, self.name ) )
      else:
         showText( "%s%s %s -> %s"  % ( index, local, self.name, self.new_name ) )

   def __show( self ):
      # get the main portion of the output
      if self.new_name is None:
         entry_string      = "%s"       % ( self.name )
      else:
         entry_string      = "%s -> %s" % ( self.name, self.new_name )
      # decode the status to decorate the string
      index, local         = self.status
      if index in _ModifiedInIndex and not local == _Unmodified:
         entry_string += '\t(%s)' % ( _StatusDescriptors[ local ] )
      # output the text
      showText( entry_string )

class Status:
   def __init__( self, repo ):
      # check to make sure the path exists and is a repo directory
      path = repo.path
      checkDir( path )
      assert isRepo( path )
      # invoke the status command and preprocess the raw data
      raw_data             = check_output( _GitStatus, path )
      raw_entries          = raw_data.splitlines()
      # transforme the data into our internal representation
      self.repo            = repo
      self.path            = path
      self.file_list       = []
      self.group_list      = {}

      # iterate through the raw entries from the 'git status'
      for raw_entry in raw_entries:
         # construct the file entry and add it to the main list
         file_item         = File( raw_entry )
         self.file_list.append( file_item )
         # iterate the group entries for this file entry
         for group_entry in file_item.groups:
            # add each to the appropriate group
            f_item, group_name, comments = group_entry
            assert f_item is file_item
            self.group_list.setdefault( group_name, [] ).append( group_entry )

   def showFiles( self ):
      # show the entries
      for entry in self.files:
         entry.dump()

   def showGroups( self, groups=_Groups, optional=False, verbose=False ):
      # iterate the global list so we show the groups in the right order
      for group_name in groups:
         # get the definition for the group
         group_def = _GroupDefs[ group_name ]
         # do we include this group?
         if group_def.required or optional:

            # look to see if there are any actual entries for this group
            if self.group_list.has_key( group_name ):
               group = self.group_list[ group_name ]

               # show the heading and the summary lines
               showHeading( group_name )
               showText( "%s (cnt=%d)" % ( colorize( group_name.upper(), *group_def.summary ), len(group) ) )

               # scan the list and find the longest descriptor
               max_len = max( [ len( fi.getDescriptor() ) for fi in self.file_list ] )
               # then scan the list again and show the results
               for group_entry in group:
                  file_item, group_name, comments = group_entry
                  file_desc = file_item.getDescriptor()
                  if len(comments):
                     showText( '%-*s  (%s)' % ( max_len, file_desc, colorizeComments( comments ) ) )
                  else:
                     showText( file_desc )
            else:
               if group_def.clean or verbose:
                  showHeading( group_name )
                  showText( getText_CLEAN() )

   def show( self, optional=False, verbose=False ):
      showAnnotated( 'Cmd', 'status' );
      self.repo.show()
      self.showGroups( optional=optional, verbose=verbose)


class Repo:
   def __init__( self, path=None ):
      # check/process the path
      if path is None:
         path        = os.getcwd()
      else:
         checkDir( path )
         path        = os.path.abspath( path )
      # set the data members
      self.cwd       = os.getcwd()
      self.path      = findRepo( path )
      self.meta      = os.path.join( self.path, _MetaDir )
      if self.path is None:
         raise exceptions.RuntimeError, "not a repository: " + repr(path)
      if path == self.path:
         self.relpath   = None
      else:
         self.relpath   = '.../%s' % path[ (len(self.path)+1) : ]
      # get the repo name
      desc = open( os.path.join( self.meta, _DescriptionFile ) )
      self.name = desc.readline().rstrip()
      desc.close
      # get the current branch
      raw_data = check_output( _GitBranches, self.path )
      for branch in raw_data.splitlines():
         if branch[0] == '*':
            self.branch = branch[2:]
            break
      else:
         raise exceptions.RuntimeError, "current branch not found"

   def status( self ):
      return Status( self )

   def show( self ):
      # showAnnotated( 'cwd',   self.cwd  )
      Root = shortenPath( self.path )
      showAnnotated( 'Root', Root )
      if self.relpath:
         showAnnotated( 'relpath', self.relpath  )
      showAnnotated( 'Name', self.name )
      showHeading( 'Branch' )
      showText( colorize( self.branch, fg=MAGENTA, bold=1 ) )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# handler functions for commands

_GitCmds          = cmdopts.Commands()

def getCommands():
   return _GitCmds

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# status options

_StatusEnv  = cmdopts.Environ( 'status' )

_StatusEnv.add( cmdopts.EnvFlag( 'verbose'  ) )
_StatusEnv.add( cmdopts.EnvFlag( 'nocolors' ) )
_StatusEnv.add( cmdopts.EnvFlag( 'optional' ) )

_StatusOpts = cmdopts.Options()

# common options
_StatusOpts.addHandler( cmdopts.EnvFlagSet(  [ '-v', '--verbose' ],     'verbose'   ) )

# command specific options
_StatusOpts.addHandler( cmdopts.EnvFlagSet(  [ '--optional' ],          'optional'  ) )
_StatusOpts.addHandler( cmdopts.EnvFlagSet(  [ '-n', '--no-colors' ],   'nocolor'   ) )

# status command

def cmdStatus( argv, env ):
   '''show current status
usage: {SCRIPT} [global options] {COMMAND} [command options]
'''
   assert argv[0] == 'status'

   repo_path   = findRepo( env.get( 'repo_path' ) )
   if repo_path:
      repo     = Repo( repo_path )
      status   = repo.status()
      verbose  = env.get( 'verbose' )
      optional = env.get( 'optional' )
      status.show( verbose=verbose, optional=optional )
   else:
      barf( 'not a repository' )
_GitCmds.add( cmdopts.Command( 'status', cmdStatus, _StatusEnv, _StatusOpts ) )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# diff command

def cmdDiff( argv, env ):
   '''show current changes
usage: {SCRIPT} [global options] {COMMAND} [command options]
'''
   assert argv[0] == 'diff'

   org_path    = env.get( 'repo_path' )
   if org_path is None:
      org_path = os.getcwd()

   if findRepo( org_path ):
      check_call( argv, org_path )
   else:
      barf( 'not a repository' )

_GitCmds.add( cmdopts.Command( 'diff', cmdDiff ) )


# vim: si
