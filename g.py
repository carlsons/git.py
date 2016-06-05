#! /usr/bin/python

'''sample ui script'''

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

import exceptions
import pprint

import git.commands

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

parsers = git.get_parsers()
args    = parsers[ 'cmdline' ].parse_args()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if args.debug:
   print 'command line arguments: '
   pprint.pprint( args.__dict__, indent=3 )
   print 'supported commands: '
   pprint.pprint( git.supported_cmdlist, indent=3 )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

if    git.global_cmdlist.has_key( args.command ):

   git.global_cmdlist[ args.command ]( parsers, args )

elif  git.supported_cmdlist.has_key( args.command ):

   git.supported_cmdlist[ args.command ].process( parsers, args )

else:

   raise exceptions.RuntimeError, "command not supported: " + repr(args.command)

