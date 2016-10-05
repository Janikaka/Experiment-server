#!/bin/bash

originalf=$1
newf=$2


# Remember to change the name afterwards to swagger.json
output="new.json"

diff $originalf $newf > patchfile.patch
patch $originalf -i patchfile.patch -o $output
rm patchfile.patch
