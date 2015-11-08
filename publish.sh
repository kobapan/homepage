#!/bin/sh
PUBLIC=_public

# project home
BASE=~/git/homepage
cd $BASE/
#

# build public
jekyll build --config __config.yml
#

# rsync to web server
############################################
# ! do this ssh thing , before rsync !
# $ ssh-keygen
# $ scp ~/.ssh/id_rsa.pub kurakazuki@kurakazuki.sakura.ne.jp:/home/kurakazuki/.ssh/authorized_keys
############################################
#
rsync -rv ${PUBLIC}/ /home/kurakazuki/www
#
