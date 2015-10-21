#!/usr/bin/env bash
# Useful tool for those confused, like me sometimes, about setuptools'
# find_packages and MANIFEST.in.
#
# Builds the package, lists its contents and removes it. You can inspect the
# files list manually. Supports wheels
#
# Usage, from repo's root dir:
#  bash bin/test_sdist_contents.bash
#
# Author: bartek.rychlicki@gmail.com
# License: no license, do whatever you want with the code.

bold=$(tput bold)
normal=$(tput sgr0)

dist_name=$(
    python setup.py sdist 2>&1\
    | egrep 'creating [0-9a-z.-]+$'\
    | cut -d' ' -f 2
)
dist_file=dist/${dist_name}.tar.gz

echo ${bold}sdist ${dist_file} contains:${normal}
tar -tf ${dist_file}
rm ${dist_file}

python setup.py bdist_wheel 2>&1 > /dev/null
bdist_file=dist/${dist_name}-*.whl

echo ${bold}bdist_wheel ${bdist_file} contains:${normal}
zip -sf ${bdist_file}
rm ${bdist_file}

echo
echo Dist files removed. Check manually if the contents match you intentions.