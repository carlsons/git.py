#! /usr/bin/zsh
FUNC_VERSION="1.13-2016.06.17-01"

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

   TEXT_UNMERGED=$(     colorize_text -b red       UNMERGED                         )
   TEXT_MODIFIED=$(     colorize_text -b yellow    MODIFIED                         )
   TEXT_UNTRACKED=$(    colorize_text -b yellow    UNTRACKED                        )

   TEXT_NOT_CONFIG=$(   colorize_text -b white     '*** NOT CONFIGURED! ***'  red   )

   TEXT_NOT_REMOTE=$(   colorize_text -b white     '*** NOT A TRACKING BRANCH! ***' red   )
   # TEXT_NOT_REMOTE=$( colorize_text    red       '*** NOT A TRACKING BRANCH! ***'       )

   TEXT_NOT_HOME=$(     colorize_text -b white     '*** NOT HOME! ***'        red   )

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
   if [ "$4" = "-n" ]; then
      echo ""
   fi
}

colorize_branch()
{
   echo $( colorize_text $BRANCH_FG_OPTS $BRANCH_FGCOLOR $1 $BRANCH_BGCOLOR )
}

show_sep()
{
   echo "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
}

show_section()
{
   if [ "$1" = "-n" ]; then
      shift
   else
      echo ""
   fi

   SECT_HEADING=$( printf "%-$((COLUMNS-2))s" $1 )

   SECT_ARGS=()
   if [ "$2" = "-b" ]; then
      SECT_ARGS+=( -b )
      shift
   fi

   colorize_text $SECT_ARGS ${2:-white} $SECT_HEADING ${3:-blue} -n

   unset SECT_HEADING
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# general helper function for indenting text
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

# general helper function for bulletizing text
bulletize_list()
{
   awk '{printf( "    * %s\n", $0 ) }'
}

# helper function to translate good statuses on a pull or push to
# the "clean" message
filter_pull_push()
{
   awk "
/^Already up-to-date.$/ || /^Everything up-to-date$/ {
   print \"${TEXT_CLEAN}\"
   next;
}
{ print }
"
}

filter_name()
{
   awk "
/^Unnamed repository/ {
   print \"${TEXT_NOT_CONFIG}\"
   next;
}
{ print }
"
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

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
git_check_dir()
{
   # git status . > /dev/null 2>&1
   git status > /dev/null 2>&1
   RC=$?
   if [ $RC -gt 1 ]; then
      barf "not a working copy"
      bomb 8
   fi
}

# climbs the directory tree up to the top-most version controlled directory
git_goto_root()
{
   while [[ ! -d .git ]];
   do
      cd ..
      [[ $PWD == '/' ]] && bomb 8
   done
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

git_get_branch()
{
awk '
/^# On branch / {
   sub( /^# On branch /, "" );
   printf( "%s", $0 );
}
'
}

git_get_home_branch()
{
   if [ -e .mergeinfo.conf ]; then
      # read the configuration
      . ./.mergeinfo.conf
      # test to make sure the source URL is define
      if [ ${+HOME_BRANCH} -eq 1 ]; then
         echo -n "$HOME_BRANCH"
      else
         echo -n "$GIT_BRANCH_CURR"
      fi
   else
      echo -n "$GIT_BRANCH_CURR"
   fi
}

# get the files that are "untracked" using the git terminology
git_get_commit_files()
{
   echo $GIT_STATUS | awk '

BEGIN {
   found = 0;
   skip  = 0;
}

/# Changes to be committed:/ {
   found = 1;
   skip  = 2;
   next;
}

( found == 0 ) { next; }
( 0 < skip )   { skip--; next; }

/#\t/ {
   # strip off the prelude
   sub( /#\t+/, "" );
   # extract the status
   status = $0;
   sub( /:.+$/, "", status );
   # extract the file
   file = $0;
   sub( /^.+: +/, "", file );
   printf( "%s\t(%s)\n", file, status );
   next;
}

{ found = 0 }
'
}

# count the untracked files
git_get_commit_cnt()
{
   git_get_commit_files | wc -l
}


# get the files that have been modified
git_get_unmerged_files()
{
   echo $GIT_STATUS | awk '

BEGIN {
   found = 0;
   skip  = 0;
}

/# Unmerged paths:/ {
   found = 1;
   skip  = 1;
   next;
}

( found == 0 ) { next; }
( 0 < skip ) && /^#$/   { skip = 0; next; }
( 0 < skip )            {           next; }

/^#\tboth modified: / {
   sub( /^#\tboth modified: +/,  "" );
   printf( "%s\t(%s)\n", $0, "both" );
   next;
}

{ found = 0 }
'
}

# count the modified files
git_get_unmerged_cnt()
{
   git_get_unmerged_files | wc -l
}


# get the files that have been modified
git_get_modified_files()
{
   echo $GIT_STATUS | awk '

BEGIN {
   found = 0;
   skip  = 0;
}

/# Changed but not updated:/ {
   found = 1;
   skip  = 2;
   next;
}

/# Changes not staged for commit:/ {
   found = 1;
   skip  = 3;
   next;
}

( found == 0 ) { next; }
( 0 < skip )   { skip--; next; }

/^#\tmodified: / {
   sub( /^#\tmodified: +/, "" );
   print;
   next;
}
/^#\tdeleted: / {
   sub( /^#\tdeleted: +/,  "" );
   printf( "%s\t(%s)\n", $0, "deleted" );
   next;
}

/^#\tunmerged: / {
   sub( /^#\tunmerged: +/,  "" );
   printf( "%s\t(%s)\n", $0, "unmerged" );
   next;
}

/^#\ttypechange: / {
   sub( /^#\ttypechange: +/,  "" );
   printf( "%s\t(%s)\n", $0, "typechange" );
   next;
}

{ found = 0 }
'
}

# count the modified files
git_get_modified_cnt()
{
   git_get_modified_files | wc -l
}

git_get_deleted_files()
{
   echo $GIT_STATUS_SHORT | grep '^ D ' | sed 's/^...//' | sort
}

git_get_untracked_files()
{
   echo $GIT_STATUS_SHORT | grep '^?? ' | sed 's/^...//' | sort
}

git_get_modified_files_all()
{
   {
      echo $GIT_STATUS_SHORT | grep '^[MAC ][MD ] ' | sed 's/^...//'
      echo $GIT_STATUS_SHORT | grep '^R'            | sed 's/^.\+ -> //'
   } | sort
}

# get the files that are "untracked" using the git terminology
_git_get_untracked_files()
{
   echo $GIT_STATUS | awk '

BEGIN {
   found = 0;
   skip  = 0;
}

/# Untracked files:/ {
   found = 1;
   skip  = 2;
   next;
}

( found == 0 ) { next; }
( 0 < skip )   { skip--; next; }

/#\t/ {
   sub( /#\t/, "" );
   print;
   next;
}

{ found = 0 }
'
}

# count the untracked files
git_get_untracked_cnt()
{
   git_get_untracked_files | wc -l
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

git_get_diff_patch()
{
   git diff --no-prefix $@
}

git_get_diff_rev_notes()
{
   cat << EOF
# revision header xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# revision summary

DETAILS:

# revision details
EOF

   if [ $COMMIT_CNT -gt 0 -o $UNMERGED_CNT -gt 0 -o $MODIFIED_CNT -gt 0 ]; then
      print "\nmodified files:"
      {
         git_get_commit_files
         git_get_unmerged_files
         git_get_modified_files
      }  | indent_text
   fi

   if [ $UNTRACKED_CNT -gt 0 ]; then
      print "\nuntracked files:"
      {
         git_get_untracked_files
      }  | indent_text
   fi

   print "\n# -=-=-=-|-=-=-=-=-|-=-=-=-=-|-=-=-=-=-|-=-=-=-=-|-=-=-=-=-|-=-=-=-=-|-=-=-=-=-|-=-=-=-=-|"
   echo $GIT_STATUS | grep '^#'
   echo "# vim: syntax=gitcommit tw=90 si"
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# helper method to verify the current revision of the working directory is clean
svn_check_revision()
{
   CHECK_REV="$( echo $1 | sed 's/[0-9]\+//g' )"
   if [ ${#CHECK_REV} -ne 0 ] ; then
      return 2
   fi
   return 0
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# helper function for doing a commit
git_commit()
{
   if $DRYRUN || $DEBUG ; then
      echo "git commit -m \"$COMMIT_MSG\""
   else
            git commit -m  "$COMMIT_MSG"
   fi
}

# wrapper function for doing an update/merge commit
git_um_commit()
{
   COMMIT_MODE=${1:-update}

   # validate and initialize the operating environment
   git_check_dir           # barfs and exists if $PWD is not a working directory
   git_goto_root           # climbs the directory tree to the root of this checkout

   # and check to make sure this is a Subversion checkout
   if [ ! -e .svn ]; then
      barf "not a Subversion checkout"
      bomb 8
   fi

   # get the Subversion revision
   SVN_REVISION=$( svnversion )
   # and verify it's up to date
   if ! svn_check_revision $SVN_REVISION ; then
      barf "Subversion checkout is NOT clean, revision: $SVN_REVISION"
      $DEBUG || bomb 2
   fi

   # get the current status
   git_get_status
   # find out what's pending in the index
   COMMIT_CNT=$( git_get_commit_cnt )
   # and die if there are no changes pending
   if [ $COMMIT_CNT -eq 0 ]; then
      barf "no changes staged to the index"
      $DEBUG || bomb 1
   fi

   # compose the commit message
   COMMIT_DATE=$( date +%Y.%m.%d-%a-%H:%M:%S-%Z )
   COMMIT_MSG="SVN ${COMMIT_MODE}: $COMMIT_DATE from r$SVN_REVISION"

   # process the request

   if $DRYRUN || $DEBUG ; then
      # call the helper; it handles $DRYRUN and $DEBUG accordingly
      git_commit
   else

      # show the commit message we're going to use
      echo "Commit Message:"
      {
         # show the commit message
         show_sep
         echo $COMMIT_MSG
         show_sep
      }  | indent_text
      echo "" # then a blank line

      # otherwise, a merge is needed and requested, so confirm; this
      # function exit if the user doesn't confirm the action
      confirm_action "commit updates to Subversion revision $SVN_REVISION"

      # and call the helper method to commit the changes
      git_commit

   fi
}


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

git_get_status()
{
   GIT_STATUS=$( git status )
   GIT_STATUS_SHORT=$( git status --short )
}

git_init_status()
{
   # validate and initialize the operating environment
   git_check_dir           # barfs and exists if $PWD is not a working directory
   git_goto_root           # climbs the directory tree to the root of this checkout

   # get the current status
   git_get_status
   GIT_BRANCH_CURR=$( echo ${GIT_STATUS} | git_get_branch )
   GIT_BRANCH_HOME=$( git_get_home_branch )
   # get various counts
   COMMIT_CNT=$(     git_get_commit_cnt      )
   UNMERGED_CNT=$(   git_get_unmerged_cnt    )
   MODIFIED_CNT=$(   git_get_modified_cnt    )
   UNTRACKED_CNT=$(  git_get_untracked_cnt   )
}

git_status()
{
   git_init_status

   # format the output

   echo " Cmd: ${1:-status}"

   ADJ_PWD=${PWD/$HOME/\~}
   echo "Root: $ADJ_PWD"
   if [ "${CURRENT_DIR}" != "${PWD}" ]; then
      ADJ_CURRENT_DIR=${CURRENT_DIR/$PWD/...}
      echo " Cwd: $( colorize_text -b red $ADJ_CURRENT_DIR )"
      unset ADJ_CURRENT_DIR
   fi
   unset ADJ_PWD

   if [ -e .git/description ] ; then
      echo "Name: $(cat .git/description | filter_name )"
   fi

   echo "Branch:"
   {
      echo -n $( colorize_branch $GIT_BRANCH_CURR )
      if [ $GIT_BRANCH_CURR != $GIT_BRANCH_HOME ]; then
         echo -n "  $TEXT_NOT_HOME"
      fi
      echo ""
   }  | indent_text

   echo "Commit:"
   {
      if [ $COMMIT_CNT -eq 0 ]; then
         echo $TEXT_CLEAN
      else
         echo "$TEXT_REQUIRED (cnt=$COMMIT_CNT)"
         git_get_commit_files    | column -t -s '	'
      fi
   }  | indent_text

   if [ $UNMERGED_CNT -gt 0 ]; then
      echo "Merge:"
      {
         echo "$TEXT_UNMERGED (cnt=$UNMERGED_CNT)"
         git_get_unmerged_files  | column -t -s '	'
      }  | indent_text
   fi

   echo "Modified:"
   {
      if [ $MODIFIED_CNT -eq 0 ]; then
         echo $TEXT_CLEAN
      else
         echo "$TEXT_MODIFIED (cnt=$MODIFIED_CNT)"
         git_get_modified_files  | column -t -s '	'
      fi
   }  | indent_text

   echo "Untracked:"
   {
      if [ $UNTRACKED_CNT -eq 0 ]; then
         echo $TEXT_CLEAN
      else
         echo "${TEXT_UNTRACKED} (cnt=$UNTRACKED_CNT)"
         git_get_untracked_files
      fi
   }  | indent_text

   if $DEBUG ; then
      echo "Output:"
      {
         echo ${GIT_STATUS}
      }  | indent_text
   fi

}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

git_pull_push()
{
   # emit the status, if verbose option is enabled
   $VERBOSE && git_status 'pull/push'

   # process the pull/push request, if it's valid

   # git the status and the current branch
   git_get_status
   GIT_BRANCH_CURR=$( echo ${GIT_STATUS} | git_get_branch )
   # get the URL of the origin; this is actually where the current repository
   # was cloned from
   GIT_ORIGIN_URL=$( git config --get remote.origin.url )
   # get the merge path within the origin that we're going to pull/push
   GIT_BRANCH_REMOTE=$( git config --get branch.${GIT_BRANCH_CURR}.remote )
   GIT_BRANCH_MERGE=$(  git config --get branch.${GIT_BRANCH_CURR}.merge  )

   # emit the origin
   if [ ${#GIT_ORIGIN_URL} -gt 0 ]; then
      echo "Origin:"
      {
         colorize_branch $GIT_ORIGIN_URL
      } | indent_text
   else
      if $VERBOSE ;then
         echo "Origin:"
         {
            echo ${TEXT_NOT_CONFIG}
         } | indent_text
      else
         echo "Origin: ${TEXT_NOT_CONFIG}"
      fi
   fi

   # emit the merge info from the remote
   if [ ${#GIT_BRANCH_REMOTE} -gt 0 ]; then
      echo "Merge:"
      {
         colorize_branch "${GIT_BRANCH_REMOTE}/${GIT_BRANCH_MERGE}"
      } | indent_text
      echo "Pull:"
      {
         git pull 2>&1  | filter_pull_push
      } | indent_text
      echo "Push:"
      {
         git push 2>&1  | filter_pull_push
      } | indent_text
   else
      if $VERBOSE ;then
         echo "Merge:"
         {
            echo ${TEXT_NOT_REMOTE}
         } | indent_text
      else
         echo "Merge:  ${TEXT_NOT_REMOTE}"
      fi
   fi

   unset GIT_STATUS
   unset GIT_BRANCH_CURR
   unset GIT_ORIGIN_URL
   unset GIT_BRANCH_REMOTE
   unset GIT_BRANCH_MERGE
}


# vim: syntax=sh
