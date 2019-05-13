#!/bin/bash

# This script needs one argument a sundew pxSender config
# It then creates a random directory /tmp/CVT****
#
# In /tmp/CVT****/.config/sarra/sender
#    you find a modified version of the sender
#    all the include files that the sender uses
#
#    The sender's config starts with some suggested sarracenia
#    config lines as if the products were to be sent from ddi.cmc
#    You can either change the resulting config or change this 
#    script to set the proper broker to use
#
#    The remaining of the sundew sender config is the same 
#    should be inspected, converted and cleaned... 
#
#    The include files remained untouched.
#
# In /tmp/CVT****/.config/sarra/plugins
#    you find all the scripts that the sender (or includes) uses
#    They must be all converted to sarracenia plugins
#
# In /tmp/CVT****/.config/sarra/credentials.conf
#    suggested credentials from the remote client found in the config 
#

# mandatory config name should

if [[ (($# != 1)) ]]; then
   echo 'error 1: need a sender config name'
   exit 1
fi

# mandatory config name has .conf

CF=`echo $1 | grep '.conf'`

if [[ -z "$CF" ]]; then
   echo 'error 2: need a sender config name'
   exit 2
fi

# mandatory sender config name is in /tx/ directory

cmd='realpath'

RP=`which realpath`
if [[  -z "$RP" ]]; then
   cmd='readlink -f'
fi

RP=`eval $cmd $1`

TX=`echo $RP | grep '/tx/'`
if [[  -z "$TX" ]]; then
   echo 'error 3: need a sender config name'
   exit
fi

# create a temporary sarra config tree

TS='/tmp/CVT'$RANDOM'/.config/sarra'
echo
echo "Creating $TS for conversion"
echo "Please visit and convert these files to sarra"
echo
mkdir -p $TS

# copy tx sender config to sarra sender config

CF=`echo $RP | sed 's/^.*tx\///'`

mkdir  $TS/sender
cp $RP $TS/sender
echo $TS/sender/$CF

# if tx sender has include ... cp to sarra sender config

TX=`echo $RP | sed 's/\/tx\/.*$/\/tx/'`

IC=`cat $RP | grep '^include' | awk '{print $2}'`

if [[ ! -z "$IC" ]]; then
	 
   IC2=''
   for INC in $IC; do
       cp $TX/$INC $TS/sender
       echo $TS/sender/$INC
       IC2=$IC2' '$TX/$INC
   done

   if [[ ! -z "$IC2" ]]; then

      #include in include ?
      IC3=`cat $IC2 | grep '^include' | awk '{print $2}'`
      for INC in $IC3; do
          cp $TX/$INC $TS/sender
          echo $TS/sender/$INC
      done
   fi
fi

# any of these configs has scripts

SC=`cat $TS/sender/* | grep '\.py$' | grep -v '^#' | sed 's/^.*=//' | sed 's/^.* //'| sort -u`

if [[ ! -z "$SC" ]]; then
   mkdir $TS/plugins

   for SCR in $SC; do
       cp $TX/../scripts/$SCR $TS/plugins
       echo $TS/plugins/$SCR
   done
fi

# credentials and destination

SCONF=$TS/sender/$CF

protocol=`cat $SCONF| grep '^protocol'    | awk '{print $2}' 2>/dev/null`
pro_host=`cat $SCONF| grep '^host'        | awk '{print $2}' 2>/dev/null`
pro_port=`cat $SCONF| grep '^port'        | awk '{print $2}' 2>/dev/null`
pro_user=`cat $SCONF| grep '^user'        | awk '{print $2}' 2>/dev/null`
pro_pass=`cat $SCONF| grep '^password'    | awk '{print $2}' 2>/dev/null`
pro_mode=`cat $SCONF| grep '^ftp_mode'    | awk '{print $2}' 2>/dev/null`
pro_keyf=`cat $SCONF| grep '^ssh_keyfile' | awk '{print $2}' 2>/dev/null`
pro_bina=`cat $SCONF| grep '^binary'      | awk '{print $2}' 2>/dev/null`

credline="${protocol}://${pro_user}"
destination=$credline

if [[ ! -z "$pro_pass" ]]; then
   credline="$credline:$pro_pass"
fi

credline="$credline@$pro_host"
destination="$destination@$pro_host"

if [[ ! -z "$pro_port" ]]; then
   credline="$credline:$pro_port"
   destination="$destination@$pro_port"
fi

if [[ "$protocol" == "sftp" ]]; then
   if [[ ! -z "$pro_keyf" ]]; then
      credline="$credline ssh_keyfile=$pro_keyf"
   fi
fi

if [[ "$protocol" == "ftp" ]]; then
   if [[ ! -z "$pro_mode" ]]; then
      if   [[ "$pro_mode" == "active" ]]; then
              credline="$credline passive=False"
      elif [[ "$pro_mode" == "passive" ]]; then
              credline="$credline passive=True"
      fi
   fi
   if [[ ! -z "$pro_bina" ]]; then
      if   [[ "$pro_bina" == "True" ]]; then
              credline="$credline binary=True"
      elif [[ "$pro_mode" == "False" ]]; then
              credline="$credline binary=False"
      fi
   fi
fi

echo $credline > $TS/credentials.conf
echo
echo $TS/credentials.conf

# suggest a sender header

cat > $TS/sender/aaa <<EOF

#==============================
# suggested sr_sender startup =
#==============================


broker amqps://feeder@ddi.cmc.ec.gc.ca/"
exchange xpublic"

instances 8"

document_root /var/www/public_data"
batch 500"

plugin pxSender_log.py

#destination
destination $destination
mirror false
EOF

echo                     >> $TS/sender/aaa
cat $TS/credentials.conf >> $TS/sender/aaa
echo                     >> $TS/sender/aaa

cat $TS/sender/$CF >> $TS/sender/aaa

mv $TS/sender/aaa $TS/sender/$CF
