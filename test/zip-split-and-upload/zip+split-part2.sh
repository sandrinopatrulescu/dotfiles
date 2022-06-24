#/bin/bash


## souce used functions and aliases
[ -z "$DOTS" ] && { echo "Error: \$DOTS is not set" && exit 1; }
source $DOTS/bashrc 1> /dev/null || { echo "Error: Couldn't source $DOTS/bashrc" && exit 1; }
shopt -s expand_aliases


# usage: $0 <zip_splits/ directory>


# example files:
# 1GiB.txt_2022-02-02_19-57-32.zip.sha256
# 1GiB.txt_2022-02-02_19-57-32.zip_splits
# 1GiB.txt_2022-02-02_19-57-32.zip_splits.sha256


# find date
object_date=$(sed -E 's@.*_([0-9]{4}(-[0-9]{2}){2}_([0-9]{2}-){2}[0-9]{2}).zip_splits/?@\1@' <<< "$1")
object=$(sed 's@(.*)_([0-9]{4}(-[0-9]{2}){2}_([0-9]{2}-){2}[0-9]{2}).zip_splits/?@\1@' <<< "$1")
object_zip=$(sed -E 's@(.*)_splits/?$@\1@' <<<"$1")




echo; echo ---\> Step 09. verify split\'s sums

dtd sha256sum -c "${object_zip}"_splits.sha256 || 
    { echo "Step 09: FAIL - splits\' checksums verification failed"; exit 1; }



echo; echo ---\> Step 10. reassemble the original

[ -e "${object_zip}" ] && 
    { echo "Step 10: FAIL - ${object_zip} already exists" && exit 1; }
date; time cat "${object_zip}"_splits/"${object_zip}"_split_* >> "${object_zip}"; date



echo; echo ---\> Step 11. check the original\'s sum


dtd sha256sum -c "${object_zip}".sha256 ||
    { echo "Step 11: FAIL - zip's checksum verification failed"; exit 1; }




echo; echo ---\> Step 12. test the zip

dtd unzip -t "${object_zip}"


[ $? -eq 0 ] && echo; echo ---\> Step 13. manually unzip the archive
