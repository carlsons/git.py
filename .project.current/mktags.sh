#! /usr/bin/zsh

get_python_files()
{
   find /usr/lib/python2.7 -type f -name '*.py'
}

get_local_files()
{
   cat files
}

{

   get_python_files

   get_local_files

} | sort | ctags -L -

