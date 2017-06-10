#!/bin/bash

# directory of the test script
DIR=$(dirname "$(readlink -f "$0")")
APP="../TrezorHash.py"
PASSPHRASE="test"
OPT=" -t -l 3 -n "  # base options
LOG=tcase.log

green=$(tput setaf 2) # green color
red=$(tput setaf 1) # red color
reset=$(tput sgr0) # revert to normal/default

GENGOLD=0 # 1...generate golden output, 0..do comparison runs
TESTPY2=1 # 1...test Python2 if installed, 0...don't test Python2
TESTPY3=1 # 1...test Python3 if installed, 0...don't test Python3

# outputs to stdout the --help usage message.
usage () {
  echo "${0##*/}: Usage: ${0##*/} [--help] [<testcasenumber> ...]"
  echo "${0##*/}: e.g. ${0##*/} 1 # run test case 1"
  echo "${0##*/}: e.g. ${0##*/} 1 2 3 # run test case 1, 2 and 3"
  echo "${0##*/}: e.g. ${0##*/} # no input will run all test cases"
}

if [ $# -eq 1 ]; then
  case "${1,,}" in
    --help | --hel | --he | --h | -help | -h | -v | --v | --version)
  	usage; exit 0 ;;
  esac
fi

function headerTrezorHashTestCase () {
    echo "Testing: Running $1 in $($py -V 2>&1)"
    rm -f $LOG
}

function trailerTrezorHashTestCase () {
    # generate golden results
    if [ $GENGOLD -eq 1 ]; then
        # echo "Generating golden results."
        for tfile in $LOG; do
            cp $tfile $1.$tfile
        done
    fi
    # comparison
    for tfile in $LOG; do
        tfile1=${tfile}.tmp.log  # without "Output:  " lines which differ from Trezor to Trezor
        tfile2=$1.${tfile}.tmp.log
        grep -v "Output: " $tfile > $tfile1
        grep -v "Output: " $1.$tfile > $tfile2
        diff $tfile1 $tfile2
        if [ $? != 0 ]; then
            echo "${red}$1 failed in $tfile diff${reset}"
        fi
        rm -f $tfile1 $tfile2
    done
    # cleanup
    pyshort=$(basename "$py")
    mv $LOG "__$pyshort.$1.$LOG"
}

function TrezorHashTestCase001 () {
    headerTrezorHashTestCase ${FUNCNAME[0]}
    $py $APP $OPT helloworld 2>> $LOG >> $LOG
    trailerTrezorHashTestCase ${FUNCNAME[0]}
}

function TrezorHashTestCase002 () {
    headerTrezorHashTestCase ${FUNCNAME[0]}
    $py $APP $OPT "hello world!" 2>> $LOG >> $LOG
    trailerTrezorHashTestCase ${FUNCNAME[0]}
}

function TrezorHashTestCase003 () {
    headerTrezorHashTestCase ${FUNCNAME[0]}
    $py $APP $OPT g4ñẽë儿 2>> $LOG >> $LOG
    $py $APP $OPT '11ñẽë儿 line1
        22ñẽë儿 line2
        33ñẽë儿 line3
        44ñẽë儿 line4
        line5' 2>> $LOG >> $LOG
    trailerTrezorHashTestCase ${FUNCNAME[0]}
}

function TrezorHashTestCase004 () {
    headerTrezorHashTestCase ${FUNCNAME[0]}
    $py $APP $OPT g4ñẽë儿 2>> $LOG >> $LOG
    $py $APP $OPT '\"\\\"\\ 11ñẽë儿 line1
        \\\\ 22ñẽë儿 line2
        \\\\\\ 33ñẽë儿 line3
        \"\" 44ñẽë儿 line4
        \\\" line5' 2>> $LOG >> $LOG
    trailerTrezorHashTestCase ${FUNCNAME[0]}
}

function TrezorHashTestCase005 () {
    headerTrezorHashTestCase ${FUNCNAME[0]}
    $py $APP $OPT -m g4ñẽë儿 "g4ñẽë儿" 2>> $LOG >> $LOG
    $py $APP $OPT -m '\"\\\"\\ 11ñẽë儿 line1
        \\\\ 22ñẽë儿 line2
        \\\\\\ 33ñẽë儿 line3
        \"\" 44ñẽë儿 line4
        \\\" line5' g4ñẽë儿 third helloworld 2>> $LOG >> $LOG
    trailerTrezorHashTestCase ${FUNCNAME[0]}
}

function TrezorHashTestCase006 () {
    headerTrezorHashTestCase ${FUNCNAME[0]}
    xsel -ib <<<"g4ñẽë儿" # this input style always terminates with \n
    rm -f ${LOG}.2
    $py $APP $OPT 2>> $LOG >> $LOG
    $py $APP $OPT "g4ñẽë儿
" 2>> ${LOG}.2 >> ${LOG}.2
    diff $LOG ${LOG}.2
    if [ $? != 0 ]; then
        echo "${red}$1 failed in ${LOG}.2a diff${reset}"
    fi
    xsel -ib <<<"g4ñẽë儿line1
line2
line3"
    $py $APP $OPT 2>> $LOG >> $LOG
    $py $APP $OPT "g4ñẽë儿line1
line2
line3
" 2>> ${LOG}.2 >> ${LOG}.2
    diff $LOG ${LOG}.2
    if [ $? != 0 ]; then
        echo "${red}$1 failed in ${LOG}.2b diff${reset}"
    fi
    rm -f ${LOG}.2
    trailerTrezorHashTestCase ${FUNCNAME[0]}
}

function TrezorHashTestCase007 () {
    headerTrezorHashTestCase ${FUNCNAME[0]}
    xsel -cb  # clear clipboard
    $py $APP $OPT "g4ñẽë儿" 2>> $LOG >> $LOG
    cbvalu=$(xsel -ob) # paste clipboard
    valu=$(grep "Output: " $LOG)
    if [ "${valu:9:3}" == "851" ] && [ "${valu:70:3}" == "39b" ]; then
        echo "${green}         Extra bonus points! Even part of the hash matches some magic numbers!${reset}"
    fi
    if [ ${#cbvalu} -ne 0 ]; then
        echo "${red}$1 failed in ${FUNCNAME[0]} length comparison (${#valu} != 0)${reset}"
    fi
    trailerTrezorHashTestCase ${FUNCNAME[0]}
}


# main
pushd $DIR > /dev/null
if [ $TESTPY2 -eq 1 ] && [ $(which python2) != "" ]; then pythonversions[2]=$(which python2); fi
if [ $TESTPY3 -eq 1 ] && [ $(which python3) != "" ]; then pythonversions[3]=$(which python3); fi
if [ $# -ge 1 ]; then
    for py in "${pythonversions[@]}"; do
        echo ""
        echo "Note   : Now performing tests with Python version $py"
        set -- "$@"
        for tcase in "$@"; do
            # is it really a valid number?
            re='^[0-9]+$'
            if ! [[ $tcase =~ $re ]] ; then
               echo "Error: $tcase is not a number. Skipping it." >&2
               continue
            fi
            fname=$(printf "TrezorHashTestCase%0*d" 3 $tcase)
            $fname
        done
        echo "End    : If no warnings or errors were echoed, then there were no errors, all tests terminated successfully."
    done
else
    # zero arguments, we run pall test cases
    echo "No argument was given. All testcases will be run. This might take up to 3 minutes."
    for py in "${pythonversions[@]}"; do
        echo ""
        echo "Note   : Now performing tests with Python version $py"
        # compgen -A function TrezorHashTestCase --> list of all functions starting with TrezorHashTestCase
        for fname in $(compgen -A function TrezorHashTestCase); do
            $fname
        done
        echo "End    : If no warnings or errors were echoed, then there were no errors, all tests terminated successfully."
    done
fi
echo
count=$(grep -i error *$LOG | wc -l)
sum=$((count))
echo "Log files contain " $count " errors."
count=$(grep -i critical *$LOG | wc -l)
sum=$((sum + count))
echo "Log files contain " $count " critical issues."
count=$(grep -i warning *$LOG | grep -v noconfirm | grep -v "If file exists it will be overwritten" | wc -l)
sum=$((sum + count))
echo "Log files contain " $count " warnings."
count=$(grep -i ascii *$LOG | wc -l)
sum=$((sum + count))
echo "Log files contain " $count " ascii-vs-unicode issues."
count=$(grep -i unicode *$LOG | wc -l)
sum=$((sum + count))
echo "Log files contain " $count " unicode issues."
count=$(grep -i latin *$LOG | wc -l)
sum=$((sum + count))
echo "Log files contain " $count " latin-vs-unicode issues."
count=$(grep -i byte *$LOG | wc -l)
sum=$((sum + count))
echo "Log files contain " $count " byte-vs-unicode issues."
if [ $sum -eq 0 ]; then
    rm -f __*.$LOG
fi
popd > /dev/null
exit 0
