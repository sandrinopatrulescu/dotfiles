#!/bin/bash

# Note: running just one single step doesn't work
#   TODO: fix it


step_choser() {
    # usage: $FUNCNAME step

    case $1 in
    
        "1")
            echo; echo ---\> Step 01. zip it &&

            dtd zip -vr "${object_zip}" "${object}"

            ;;
        "2")
            echo; echo ---\> Step 02. test the zip &&

            dtd unzip -t "${object_zip}" | tee --append "${object_zip}"_unzip-test_output.txt &&

            echo && 
            grep "No errors detected" "${object_zip}"_unzip-test_output.txt ||
                { echo "Step 2: FAIL: unzip -t detected errors"; return 1; }

            ;;
        "3")
            echo; echo ---\> Step 03. split the zip file &&

            mkdir "${object_zip}"_splits &&
                dtd split --verbose --bytes="$split_size" "${object_zip}" "${object_zip}"_splits/"${object_zip}"_split_

            ;;
        "4")
            echo; echo ---\> Step 04. reassemble the splits and test the result &&

            [ -e "${object_and_date}"_reassembled.zip ] && { echo "Step 04: FAIL - ${object_and_date}_reassembled.zip already exists" && return 1; }
            date; time cat "${object_zip}_splits/${object_zip}"_split_* >> "${object_and_date}"_reassembled.zip; date


            echo; echo "Reassembling done. Now testing the reassembled zip file"; echo


            dtd unzip -t "${object_and_date}"_reassembled.zip | tee --append "${object_and_date}"_reassembled.zip_unzip-test_output.txt &&

            echo

            grep "No errors detected" "${object_and_date}"_reassembled.zip_unzip-test_output.txt ||
                { echo "Step 4: FAIL: unzip -t detected errors"; return 1; }

            ;;
        "5")
            echo; echo ---\> Step 05. compute original zip\'s checksum and verify it &&

            date; time sha256sum "${object_zip}" >| "${object_zip}".sha256; date &&


            echo && echo "Computing checksum is done. Now verifying it"; echo &&

            { dtd sha256sum -c "${object_zip}".sha256 ||
                { echo "Step 05: FAIL - checksum verification failed"; return 1; } }

            ;;
         "6")
            echo; echo ---\> Step 06. compute splits\' checksums and verify them &&

            date; time sha256sum "${object_zip}_splits/${object_zip}"_split_* > "${object_zip}"_splits.sha256; date &&


            echo && echo "Computing splits' checksums is done. Now verifying them"; echo &&

            { dtd sha256sum -c "${object_zip}"_splits.sha256 || 
                { echo "Step 06: FAIL - splits' checksum verification failed"; return 1; } }

            ;;
        "7")
            echo; echo ---\> Step 07. UPLOAD
            echo "${object_zip}".sha256
            echo "${object_zip}"_splits.sha256
            echo "${object_zip}"_splits
            echo "    and continue with part 2"


            ;;
        "8")
            echo; echo ---\> Step 08. DOWNLOAD
            echo "${object_zip}".sha256
            echo "${object_zip}"_splits.sha256
            echo "${object_zip}"_splits
            echo "    and continue with part 2"

            ;;
        *)
            echo "Error: No such step exists" && return 1
            ;;

    esac

}


# Pre-Run Phase
unset step
no_of_steps="8"
split_size="128M"

## check command line arguments
[ -e "$1" ] && object="$1" || { echo "usage: $0 <file/dir> [step]" && exit 1; }
[ $# -eq 2 ] && { 
    grep -qE "^[0-9]+$" <<< "$2" || 
        { echo "Error: -step- must be an int" && exit 1; }
    step="$2"
}



## souce used functions and aliases
[ -z "$DOTS" ] && { echo "Error: \$DOTS is not set" && exit 1; }
source $DOTS/bashrc 1> /dev/null || { echo "Error: Couldn't source $DOTS/bashrc" && exit 1; }
shopt -s expand_aliases


## set variables to use for file names
create_date=$(fdate)
object_and_date="${object}_${create_date}"
object_zip="${object_and_date}.zip"


## set the title
title &&
    TITLE="${TITLE}: ${object} zip + split" &&
    title "${TITLE}" &&
    echo "\$TITLE=${TITLE}"


# Run Phase


[ -z "$step" ] && {
    for s in $(seq $no_of_steps); do
        step_choser "$s"
    done
} ||
    step_choser "$step"







