#! /usr/bin/zsh
FUNC_VERSION="1.7-2014.10.30-01"

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

init_text()
{
   if ${COLORS:-true} ; then
      autoload colors
      colors
   fi

   TEXT_DEBUG=$(        colorize_text -b red       DEBUG                            )
   TEXT_DRYRUN=$(       colorize_text -b red       DRY-RUN                          )

   TEXT_CLEAN=$(        colorize_text -b green     CLEAN                            )
   TEXT_RECOMMENDED=$(  colorize_text -b yellow    RECOMMENDED                      )
   TEXT_REQUIRED=$(     colorize_text -b red       REQUIRED                         )
   TEXT_BLOCKED=$(      colorize_text -b red       BLOCKED                          )

   TEXT_CONFLICT=$(     colorize_text -b red       CONFLICTS                        )
   TEXT_MODIFIED=$(     colorize_text -b yellow    MODIFIED                         )
   TEXT_UNTRACKED=$(    colorize_text -b yellow    UNTRACKED                        )

   TEXT_NOT_CONFIG=$(   colorize_text -b white     '*** NOT CONFIGURED! ***'  red   )

   TEXT_NOT_FOUND=$(    colorize_text -b white     '*** NOT FOUND! ***'       red   )

   BRANCH_FG_OPTS='-b'
   BRANCH_FGCOLOR='magenta'
   BRANCH_BGCOLOR='black'

}

colorize_text()
{
   # echo -n "$fg_bold[${1}]${2}$reset_color"
   if [ "$1" = "-b" ]; then
      shift
      echo -n "$fg_bold[${1}]"
   else
      echo -n "$fg[${1}]"
   fi
   [ $# -gt 2 ] && echo -n "$bg[${3}]"
   echo -n "${2}"
   echo -n "$reset_color"
}

colorize_branch()
{
   echo $( colorize_text $BRANCH_FG_OPTS $BRANCH_FGCOLOR $1 $BRANCH_BGCOLOR )
}

show_sep()
{
   echo "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
}

set_url()
{
   case ${1:-raptor} in

      raptor)  REPO_URL="${REPO_ROOT}/raptor"          ;;
      tools)   REPO_URL="${REPO_ROOT}/tools"           ;;
      docs)    REPO_URL="${REPO_ROOT}/docs"            ;;

      *)       barf_and_die "repository '${1}' not known"   ;;

   esac
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

count_lines()
{
   awk '
BEGIN { CNT = 0   }
      { CNT+=1    }
END   { print CNT }
'
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# helper function for extracting an annotated value
get_annotated_value()
{
   # grep "^$1: " | sed "s/^$1: //"
   awk "
BEGIN {
   found=0;
}
/^$1: / {
   sub( /^$1: /, \"\" );
   print;
   found=1;
}
END {
   if ( ! found )
   {
      print \"${2:-NIL}\";
   }
}
"
}

# general helper functino for indenting text
indent_text()
{
   awk '
(0 < NF) {
   printf( "%3s%s\n", "", $0 );
   next;
}
{
   print
}
'
}

# helper method, if not debugging, it confirms "are you sure" and exits if the
# answer is negative
confirm_action()
{
   if ! $DEBUG ; then

      barf $@

      unset ANSWER
      vared -c -p "are you sure? " ANSWER
      [ $? -eq 0 ] || exit 1

      case ${(L)ANSWER} in

         yes)
            # continue
         ;;

         n*)
            barf "aborted!"
            exit 1
         ;;

         *)
            barf "invalid answer!"
            exit 2
         ;;

      esac
   fi
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# check to make sure the current directory is a working copy
svn_check_dir()
{
   svn info . > /dev/null 2>&1 || { barf "not a working copy" ; bomb 8 }
}

# climbs the directory tree up to the top-most version controlled directory
svn_goto_root()
{
   while [ -d ../.svn ];
   do
      cd ..
   done
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# filters the svn-info to retrieve interesting data

svn_filter_headings()
{
awk '
# /^Path:/                { print }
/^URL:/                 { printf " "; print }
/^Repository UUID:/     { sub( /^Repository /, "" ); print }
'
}

svn_filter_base()
{
awk '
# /^Revision:/            { print }
/^Last Changed Date:/   { print }
'
}

svn_filter_head()
{
awk '
/^Revision:/            { print }
/^Last Changed Rev:/    { print }
/^Last Changed Date:/   { print }
'
}

format_status()
{
awk '
{ print }
END { if ( FNR == 0 ) { print "No changes pending" } }
'
}

svn_format_mergelog()
{
awk '

# skip to the Log line, which is supposed to be the first line of the
# mergelog file
/^ Log: / {
   found = 1;
}
( found == 0 ) { next; }

# process the text

/^ Log: / {
   sub( /^ Log: /, "" );      # strip the leading stuff
   print                      # print the header
   print ""                   # and skip a blank line
   next;
}

( NF == 0 ) { next; }         # skip blank lines

/^--- Merging/ {
   sub( /^--- /, "" );        # strip off the leading stuff
   sub( /:$/,    "" );        # and the trailing stuff

   print "Partial output:"
   printf( "   %s\n\n", $0 ); # and print the line
   exit
}

{ print }

'
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

svn_get_repo_name()
{
   echo $@ | awk "

/^svn:\/\// {
   # split the URL into three pieces: the protocol, the server and URN
   match( \$0, /([[:alnum:]]+):\/\/([^\/]+)\/(.*)/, vals )
   # printf( \"%s,%s,%s\", vals[1], vals[2], vals[3] )
   URN = vals[3]
}

/\/trunk\>/ {

   root = URN
   sub( /\/trunk.*/, \"\", root )           # strip off the trailing stuff
   gsub(   /[[:alnum:]_]+\//,  \"\", root ) # strip all the leading names

   printf( \"%s/trunk\", root )

   next
}

/\/branches\>/ {

   root = URN
   sub( /\/branches.*/, \"\", root )        # strip off the trailing stuff
   gsub(   /[[:alnum:]_]+\//,  \"\", root ) # strip all the leading names

   branch = URN
   sub( /.*\/branches\//, \"\", branch )    # strip off the trailing stuff

   printf( \"%s/%s\", root, branch )

   next
}

/^svn:\/\// {

   sub( /\/?[[:alnum:]_]+$/,   \"\", URN ) # strip the last name, provided by the path
   gsub(   /[[:alnum:]_]+\//,  \"\", URN ) # strip all the leading names

   printf( \"%s/\", URN )
}

/^file:\/\// {
   URN = \$0
   gsub(   /.+\//,  \"\", URN ) # strip all the leading names
   printf( \"local/%s\", URN )
}
"
}

svn_get_version()
{
   svnversion | sed 's/M$//'
}

svn_get_externals()
{
   svn status | awk "
/^Performing status on external item at / {
   sub( /^.+ at '/, \"\" );
   sub( /'.*$/, \"\" );
   print
}
"
}

svn_get_externals_cnt()
{
   svn_get_externals | wc -l
}

# functions to deal with "modified" files

# get the files that have been modified in the working directory
svn_get_modified_files()
{
   svn status | awk '
( NF == 0 ) { next }
/^?/ { next }
/^X/ { next }
/^Performing status on external item at / { next }
{ print }
'
}

# count the modified files
svn_get_modified_cnt()
{
   svn_get_modified_files | wc -l
}

svn_get_modified_file_names()
{
   svn_get_modified_files | grep '^M ' | sed 's/^M \+//'
}

# functions to deal with "conflict" files

# get the files that have pending conflicts in the working directory
svn_get_conflict_files()
{
   svn status | awk '
( NF == 0 ) { next }
/^?/ { next }
/^X/ { next }
/^Performing status on external item at / { next }
/^C/ { print }
' | sort
}

# count the conflict files
svn_get_conflict_cnt()
{
   svn_get_conflict_files | wc -l
}

svn_get_conflict_file_names()
{
   svn_get_conflict_files | grep '^C ' | sed 's/^C \+//'
}

# functions to deal with "untraced" files

# get the files that are "untracked" using the git terminology
svn_get_untracked_files()
{
   svn status | awk '
/^?/ { sub( /^? +/, "" ); print }
{ next }
'
}

# count the untracked files
svn_get_untracked_cnt()
{
   svn_get_untracked_files | wc -l
}

svn_get_update_files()
{
   svn status -u 2>/dev/null                 \
      | grep '^.\+\*'                        \
      | sed 's/^[M]\? \+\* \+[0-9]\+ \+//'   \
      | sed 's/^[M]\? \+\* \+//'             \
      | sort
}

# count the number of files to be updated
svn_get_update_cnt()
{
   svn_get_update_files | wc -l
}

# get the eligible revisions that can be merged from the given source
svn_get_merge_revs()
{
   svn mergeinfo --show-revs=eligible $1
}

# look at the state of the current working directory
svn_get_mergeinfo()
{
   MERGE_CONFIGURED='false'
   MERGE_BLOCKED='false'
   MERGE_NEEDED='false'
   MERGE_BLOCKS=()
   ACTIONS=()

   # validate and initialize the operating environment
   svn_check_dir           # barfs and exists if $PWD is not a working directory
   svn_goto_root           # climbs the directory tree to the root of this checkout

   # step 1 - check for local changes that would need to be commited

   # find out how many changes are pending
   MODIFIED_CNT=$(   svn_get_modified_cnt    )
   UNTRACKED_CNT=$(  svn_get_untracked_cnt   )
   # and update the status
   if [ $MODIFIED_CNT -gt 0 ]; then
      CHANGE_STATUS="$TEXT_REQUIRED (cnt=$MODIFIED_CNT)"
      MERGE_BLOCKED='true'
      MERGE_BLOCKS+=( "commit" )
      ACTIONS+=( "commit" )
   else
      CHANGE_STATUS="$TEXT_CLEAN"
   fi

   # step 2 - check for commits to the current branch that need to be updated

   # get the info for the BASE and the HEAD
   SVN_BASE=$( svn info -r BASE . )
   SVN_HEAD=$( svn info -r HEAD . )
   # get the PATH variable from the HEAD
   SVN_PATH=$( echo $SVN_HEAD | get_annotated_value 'Path'              "" )
   # get the various revision numbers we need
   REV_CURR_SVN=$( svn_get_version )
   REV_CURR=$( echo $SVN_BASE | get_annotated_value 'Revision'          0  )
   REV_NEED=$( echo $SVN_HEAD | get_annotated_value 'Last Changed Rev'  0  )
   REV_HEAD=$( echo $SVN_HEAD | get_annotated_value 'Revision'          0  )
   # check the revisions to see if we need to update the current working directory
   if [ $REV_CURR -lt $REV_HEAD ]; then
      UPDATE_STATUS="$TEXT_REQUIRED ($REV_CURR -> $REV_HEAD)"
      MERGE_BLOCKED='true'
      MERGE_BLOCKS+=( "update" )
      ACTIONS+=( "update" )
   elif  [ $REV_CURR != $REV_CURR_SVN ]; then
      UPDATE_STATUS="$TEXT_REQUIRED ($REV_CURR_SVN)"
      MERGE_BLOCKED='true'
      MERGE_BLOCKS+=( "update" )
      ACTIONS+=( "update" )
   else
      UPDATE_STATUS="$TEXT_CLEAN"
   fi

   # step 3 - check for any commits to the trunk that need to be merged

   if [ -e .mergeinfo.conf ]; then
      # read the configuration
      . ./.mergeinfo.conf
      # test to make sure the source URL is define
      if [ ${+MERGE_FROM_URL} -eq 1 ]; then
         MERGE_CONFIGURED='true'
      else
         barf "merge from URL not defined"
      fi
   fi

   if $MERGE_CONFIGURED ; then

      # get the eligible revisions
      MERGE_HEAD=$( svn info -r HEAD $MERGE_FROM_URL )
      MERGE_REVS=( $( svn_get_merge_revs $MERGE_FROM_URL ) )
      MERGE_CNT=${#MERGE_REVS} 
      MERGE_PATH=$(     echo $MERGE_HEAD | get_annotated_value 'Path'      "" )
      MERGE_REV_HEAD=$( echo $MERGE_HEAD | get_annotated_value 'Revision'  0  )
      # and update the status
      if [ $MERGE_CNT -gt 0 ]; then
         MERGE_STATUS="$TEXT_REQUIRED (cnt=$MERGE_CNT)"
         MERGE_NEEDED='true'
         if $MERGE_BLOCKED ; then
            ACTIONS+=( "merge (BLOCKED)" )
         else
            ACTIONS+=( "merge" )
         fi
      else
         MERGE_STATUS="$TEXT_CLEAN"
      fi

   else
      MERGE_STATUS="$TEXT_NOT_CONFIG"
   fi
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# test the current working directory and return a value that represents
# the current status
svn_merge_test()
{
   # setup the environment
   svn_get_mergeinfo
   # return an exit code that reflects the current status
   $MERGE_CONFIGURED || return 3 # if *NOT* configured
   $MERGE_BLOCKED    && return 2 # if blocked
   $MERGE_NEEDED     || return 1 # if *NOT* needed
   return 0                      # otherwise it's needed
}

svn_merge_header()
{
   $DRYRUN && echo "Mode: $TEXT_DRYRUN"
   $DEBUG  && echo "Mode: $TEXT_DEBUG"
   echo " Log: MERGE;ALL;$SVN_PATH;pulled $MERGE_CNT revisions from $MERGE_PATH through r$MERGE_REV_HEAD"
   echo " Cmd: merge"
   echo "Date: $RUN_DATE"
   echo "Path: $MERGE_PATH"
   echo " URL: $MERGE_FROM_URL"
   echo "Head: $MERGE_REV_HEAD"
   echo " Cnt: $MERGE_CNT"
   echo "Revs: "
   echo "${(j:, :)MERGE_REVS}" | fold -s -w66 | indent_text
   echo ""
}

svn_merge()
{
   # show the header block
   svn_merge_header

   ARGS=( --accept postpone )
   $DRYRUN && ARGS+=( --dry-run )

   if $DEBUG; then
      # --debug mode just shows the command
      echo "svn merge $ARGS $MERGE_FROM_URL"
   else
            svn merge $ARGS $MERGE_FROM_URL
   fi

}

# helper function for doing a commit
svn_commit()
{
   if $DRYRUN || $DEBUG ; then
      echo "svn commit -F $1"
   else
            svn commit -F $1
   fi
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# augmented "svn mergeinfo" command
svn_mergeinfo()
{
   # setup the environment
   svn_get_mergeinfo

   # step 4 - output the summary
   echo " Cmd: mergeinfo"
   echo "Root: ${PWD/$HOME/~}"
   echo $SVN_HEAD | svn_filter_headings
   echo "Path: $( colorize_branch $SVN_PATH )"

   echo "Commit:"
   {
      echo "$CHANGE_STATUS"
      [ $UNTRACKED_CNT -gt 0 ] && echo "${TEXT_UNTRACKED} (cnt=$UNTRACKED_CNT)"
   }  | indent_text

   echo "Update:"
   {
      echo "$UPDATE_STATUS"
   } | indent_text

   echo "Merge:"
   {
      echo "$MERGE_STATUS"
      if $MERGE_CONFIGURED ; then
         echo "From:"
         {
            echo " URL: $MERGE_FROM_URL"
            echo "Head: $MERGE_REV_HEAD"
            if $VERBOSE && $MERGE_NEEDED ; then
               echo "Revision(s): "
               echo "${(j:, :)MERGE_REVS}" | fold -s -w66 | indent_text
            fi
         }  | indent_text
      fi
   } | indent_text

   if $MERGE_CONFIGURED ; then
      echo "Actions:"
      {
         if [ ${#ACTIONS} -eq 0 ]; then
            echo "none"
         else
            echo ${(j:, :)ACTIONS}
         fi

      } | indent_text
   fi
}

# helper function
show_svn_status()
{

   # get the info for the BASE and the HEAD
   SVN_BASE=$( svn info -r BASE . )
   SVN_HEAD=$( svn info -r HEAD . 2>/dev/null )
   [ ${#SVN_HEAD} -gt 0 ] && SVN_HEAD_OK='true' || SVN_HEAD_OK='false'
   # get the PATH variable from the HEAD
   SVN_PATH=$( echo $SVN_HEAD | get_annotated_value 'Path'              "" )
   SVN_URL=$(  echo $SVN_HEAD | get_annotated_value 'URL'               "" )
   SVN_REPO_NAME=$( svn_get_repo_name $SVN_URL )
   # get the various revision numbers we need
   REV_CURR_SVN=$( svn_get_version )
   REV_CURR=$( echo $SVN_BASE | get_annotated_value 'Revision'          0  )
   REV_NEED=$( echo $SVN_HEAD | get_annotated_value 'Last Changed Rev'  0  )
   REV_HEAD=$( echo $SVN_HEAD | get_annotated_value 'Revision'          0  )
   # count the number of local changes pending
   UPDATE_LST=$(     svn_get_update_files       )  # get the list once
   UPDATE_CNT=$(     echo -n $UPDATE_LST | count_lines )  # and count them here
   CONFLICT_CNT=$(   svn_get_conflict_cnt       )
   MODIFIED_CNT=$(   svn_get_modified_cnt       )
   UNTRACKED_CNT=$(  svn_get_untracked_cnt      )
   # pick up the base path
   SVN_BASE_PATH=$( echo $SVN_BASE | get_annotated_value 'Path'         "" )
   # get external linkages
   EXTERNALS_CNT=$(  svn_get_externals_cnt      )

   # and format the output

   echo " Cmd: ${1:-status}"

   ADJ_PWD=${PWD/$HOME/\~}
   echo "Root: $ADJ_PWD"
   if [ "${CURRENT_DIR}" != "${PWD}" ]; then
      ADJ_CURRENT_DIR=${CURRENT_DIR/$PWD/...}
      echo " Cwd: $( colorize_text -b red $ADJ_CURRENT_DIR )"
      unset ADJ_CURRENT_DIR
   fi
   unset ADJ_PWD

   if $SVN_HEAD_OK ; then
      echo $SVN_HEAD       | svn_filter_headings
      SVN_REPO_DESC="$SVN_REPO_NAME"
      # SVN_REPO_DESC="$SVN_PATH"
      # SVN_REPO_DESC="${SVN_REPO_NAME}${SVN_PATH}"
      echo "Path: $( colorize_branch $SVN_REPO_DESC )"
   else
      echo "Head: ${TEXT_NOT_FOUND}"
      echo $SVN_BASE       | svn_filter_headings
      echo "Path: $( colorize_branch $SVN_BASE_PATH )"
   fi

   echo "Base:"
   {
      echo "Revision: $(svnversion)"
      echo $SVN_BASE    | svn_filter_base
   }  | indent_text

   if $SVN_HEAD_OK ; then

      echo "Head:"
      {
         echo $SVN_HEAD    | svn_filter_head
      }  | indent_text

      echo "Update:"
      {

         if  [ $REV_CURR -lt $REV_NEED ]; then
            echo "$TEXT_REQUIRED ($REV_CURR -> $REV_NEED)"
         elif  [ $REV_CURR -lt $REV_HEAD ]; then
            echo "$TEXT_RECOMMENDED ($REV_CURR -> $REV_HEAD)"
         elif  [ $REV_CURR != $REV_CURR_SVN ]; then
            echo "$TEXT_RECOMMENDED ($REV_CURR_SVN)"
         else
            echo "$TEXT_CLEAN"
         fi

         [ $UPDATE_CNT -gt 0 ] && echo "Files: $UPDATE_CNT"

         $VERBOSE && echo -n $UPDATE_LST

      }  | indent_text
   fi

   if [ $CONFLICT_CNT -gt 0 ]; then
      echo "Conflicts:"
      {
         echo "$TEXT_CONFLICT (cnt=$CONFLICT_CNT)"
         svn_get_conflict_files
      }  | indent_text
   fi

   echo "Modified:"
   {
      if [ $MODIFIED_CNT -eq 0 ]; then
         echo $TEXT_CLEAN
      else
         echo "$TEXT_MODIFIED (cnt=$MODIFIED_CNT)"
         svn_get_modified_files
      fi
   }  | indent_text

   echo "Untracked:"
   {
      if [ $UNTRACKED_CNT -eq 0 ]; then
         echo $TEXT_CLEAN
      else
         echo "${TEXT_UNTRACKED} (cnt=$UNTRACKED_CNT)"
         svn_get_untracked_files
      fi
   }  | indent_text

}

# augmented "svn status" command
svn_status()
{
   # validate and initialize the operating environment
   svn_check_dir           # barfs and exists if $PWD is not a working directory
   svn_goto_root           # climbs the directory tree to the root of this checkout

   show_svn_status

   if [[ $EXTERNALS_CNT -gt 0 ]]; then

      echo "$( colorize_text -b magenta 'EXTERNAL:' )"
      {
         svn_get_externals
      }  | indent_text

      if $VERBOSE ; then
         svn_get_externals | while read EXTERNAL
         do
         (
            show_sep
            cd $EXTERNAL
            CURRENT_DIR=$PWD
            show_svn_status 'status/EXTERNAL'
         )
         done
      fi

   fi


}


# vim: syntax=sh si
