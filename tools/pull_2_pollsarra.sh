#!/bin/bash

# SPECIFIC FOR DDSR.CMC.EC.GC.CA
# just make sure the resulting poll/sarra config
# corresponds to your site

conf=`echo $1| sed 's/^.*\///' | sed 's/.conf//'`

POLL="poll_${conf}.conf"

vi -c '1,/^type/-1w!./doc' -c q  $1
cat ./doc > $POLL

cat >> $POLL << EOF

# on doit avoir le vip de ddsr.cmc.ec.gc.ca

vip 142.135.12.146

# post_broker is DDSR spread the poll messages

post_broker amqp://SOURCE@ddsr.cmc.ec.gc.ca/
post_exchange xs_SOURCE

# options

EOF

echo sleep `cat $1 | grep ^pull_sleep | awk '{print $2}' 2> /dev/null` >> $POLL
echo timeout `cat $1 | grep ^timeout_get | awk '{print $2}' 2> /dev/null` >> $POLL

echo >> $POLL

cat >> $POLL << EOF2

# to useless... left for backward compat
to DDSR.CMC,DDI.CMC,CMC,SCIENCE,EDM

# where to get the products

EOF2

protocol=`cat $1| grep '^protocol'    | awk '{print $2}' 2>/dev/null`
pro_host=`cat $1| grep '^host'        | awk '{print $2}' 2>/dev/null`
pro_port=`cat $1| grep '^port'        | awk '{print $2}' 2>/dev/null`
pro_user=`cat $1| grep '^user'        | awk '{print $2}' 2>/dev/null`
pro_pass=`cat $1| grep '^password'    | awk '{print $2}' 2>/dev/null`
pro_mode=`cat $1| grep '^ftp_mode'    | awk '{print $2}' 2>/dev/null`
pro_keyf=`cat $1| grep '^ssh_keyfile' | awk '{print $2}' 2>/dev/null`
pro_bina=`cat $1| grep '^binary'      | awk '{print $2}' 2>/dev/null`

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

echo $credline > ./credentials

echo "destination $credline"              >> $POLL
echo                                      >> $POLL
echo "#where/how to get the products"     >> $POLL
echo                                      >> $POLL

vi -c '/^extension/+1,$w!./dir' -c q $1
cat ./dir >> $POLL
rm ./dir

cat >> $POLL << EOF3

# ==============================l
# usually no accept... in sr_poll

EOF3

cat $1 | grep -v ^#  >> $POLL


#========= now sarra =============


SARRA="sarra_get_${conf}.conf"
cat ./doc > $SARRA
rm ./doc

cat >> $SARRA << EOF4

# source

instances 1

# receives messages from same DDSR queue spreads the messages

broker amqp://feeder@ddsr.cmc.ec.gc.ca/
exchange   xs_SOURCE

# listen to spread the poll messages

prefetch  10
queue_name q_feeder.\${PROGRAM}.\${CONFIG}.SHARED

source_from_exchange True

# what to do with product

mirror        False
preserve_time False

EOF4

echo '# MG CHECK DELETE' >> $SARRA
echo '#delete' `cat $1 | grep ^delete | awk '{print $2}' 2> /dev/null` >> $SARRA
echo delete False >> $SARRA

cat >> $SARRA << EOF5

# directories

directory \${PBD}/\${YYYYMMDD}/\${SOURCE}/--\${0}-- to be determined ----
accept    .*(something).*

# destination

post_broker   amqp://feeder@localhost/
post_exchange xpublic
post_base_url http://\${HOSTNAME}
post_base_dir /apps/sarra/public_data

EOF5
