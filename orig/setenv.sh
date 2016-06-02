#! /usr/bin/zsh
TEMPLATE_VERSION="1.1-2016.05.24-01"

SCRIPT_VERSION="1.1-2016.05.24-01"
SCRIPT_NAME="setenv.sh"
SCRIPT_DESC="Environment"

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# global functions, needed during initialization

get_real_pwd()
{
   (
      cd $1
      pwd -P
   )
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# set the template environment

CURRENT_DIR="$PWD"

SCRIPT="$0"
SCRIPT_BASENAME="$( basename ${SCRIPT} )"
SCRIPT_PATHNAME="$( dirname  ${SCRIPT} )"
SCRIPT_PID=$$

SCRIPT_ARGS=( $@ )

DATE_SPEC='+%Y.%m.%d-%a-%H.%M.%S-%Z'
RUN_DATE=$( date $DATE_SPEC )

LOCALHOST=$( hostname )
LOCALHOST_FDQN=$( hostname -f )

VERBOSE='false'
DEBUG='false'

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# if we're being run from a link, canonicalize the link so we know where we're
# really running from; otherwise, translate the path to a fully qualified path

REAL_SCRIPT="${SCRIPT}"
REAL_BASENAME="${SCRIPT_BASENAME}"
REAL_PATHNAME="${SCRIPT_PATHNAME}"

if [ -L ${SCRIPT} ]; then

   REAL_SCRIPT=$( readlink --canonicalize-existing ${SCRIPT} )
   REAL_BASENAME="$( basename ${REAL_SCRIPT} )"
   REAL_PATHNAME="$( dirname  ${REAL_SCRIPT} )"

else

   REAL_PATHNAME=$( get_real_pwd ${REAL_PATHNAME} )

fi

alias gg="${REAL_PATHNAME}/g.py"

