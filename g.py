#! /usr/bin/python

'''sample ui script'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

import exceptions
import pprint
import os

import scm
import git.commands
import svn.commands

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

parsers = {}

parsers[ 'root' ]    = scm.get_root_parser()

parsers[ 'global' ]  = scm.get_global_parser( parsers[ 'root' ] )
global_args          = parsers[ 'global' ].parse_args()

if global_args.root is None:
   global_args.root = os.getcwd()

parsers[ 'cmdline' ] = scm.get_cmdline_parser( parsers[ 'root' ], git.supported_cmdlist )
cmdline_args         = parsers[ 'cmdline' ].parse_args()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if cmdline_args.debug:
   print 'global arguments: '
   pprint.pprint( global_args.__dict__, indent=3 )
   print 'cmdline arguments: '
   pprint.pprint( cmdline_args.__dict__, indent=3 )
   print 'supported Git commands: '
   pprint.pprint( git.supported_cmdlist, indent=3 )
   print 'supported Subversion commands: '
   pprint.pprint( svn.supported_cmdlist, indent=3 )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if cmdline_args.command is None:
   cmdline_args.command = "status"

if    scm.global_cmdlist.has_key( cmdline_args.command ):

   scm.global_cmdlist[ cmdline_args.command ]( parsers, cmdline_args )

elif  git.supported_cmdlist.has_key( cmdline_args.command ):

   git.supported_cmdlist[ cmdline_args.command ].process( parsers, cmdline_args )

else:

   raise exceptions.RuntimeError, "command not supported: " + repr(cmdline_args.command)

