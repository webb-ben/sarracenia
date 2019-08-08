==========
 MIGRATION
==========

-------------------------------------------
Sundew sender migration to sarracenia (PXATX)
-------------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sarracenia Suite

.. contents::

DESCRIPTION
===========

This document was written right after my presentation of August 8th.
It will basically be a summary of what was said for the sundew sender
migration part of it.

In order to make a right reference from sundew table routings and sender 
configuration options, I suggest a setup and some tools. It is to be taken
as a suggestion. I have heavily used a similar setup on my desktop in
the conversion of sundew pull to sarra poll-sarra pairs. I have also used
one of the sender script to convert simple sender from pxatx (or sundew in
fact too) that requiered to be migrated to sarra in the mist of that
conversion.  

SETUP
=====

After having poke the several clusters (sundew and sarra) with tools
on data-lb-ops1 (under users px and sarra)... it was so annoying that
I decided one day to get all the information (from this date) available
on all the clusters and work from my desktop. I am convinced that it
strikes you as simpler than the tasks underlined above.

In order to use scripts provided as is, it would be better to use
the same setup as I was using when developping/using them. Of course,
this is not mandatory, and should you prefer other setups, you can
do so and modify the scripts accordingly... or write you own... I
dont mind, I just present/propose some tools that I have used.

So my setup was::

     mkdir ~/convert

     # and in this directory you place

     ~/convert
     │
     ├── tools
     │   ├── compare.sh
     │   ├── do_this_pull.sh
     │   ├── do_this_sender.sh
     │   ├── pull_2_pollsarra.sh
     │   ├── pxsender_2_sarra.sh
     │   ├── sr_sender_one_day.sh
     │   └── sundew_routing_2_sarra_subtopic.py
     │
     ├── plugins
     │   ├── msg_from_file.py
     │   └── pxSender_log.py
     │
     ├── config
     │   │
     │   ├── pxatx
     │   │   └── etc
     │   │       ├── rx
     │   │       ├── fx
     │   │       ├── scripts
     │   │       ├── trx
     │   │       ├── tx
     │   │       └── ...
     │   │
     │   ├── sundew
     │   │   └── etc
     │   │       ├── rx
     │   │       ├── fx
     │   │       ├── scripts
     │   │       ├── trx
     │   │       ├── tx
     │   │       └── ...
     │   │
     │   └── sarra
     │           ├── cpost
     │           ├── plugins
     │           ├── poll
     │           ├── post
     │           ├── sarra
     │           ├── sender
     │           ├── shovel
     │           └── watch
     │
     ├── log 
     │   │
     │   ├── pxatx
     │   │   └── ...
     │   │
     │   ├── sr_pxatx
     │   │   └── ...
     │   │
     │   ├── ddsr (sarra)
     │   │   ├── px2-ops
     │   │   ├── px3-ops
     │   │   ├── px4-ops
     │   │   ├── px5-ops
     │   │   ├── px6-ops
     │   │   ├── px7-ops
     │   │   └── px8-ops
     │   │
     │   └── sundew
     │       ├── px2-ops
     │       ├── px3-ops
     │       ├── px4-ops
     │       ├── px5-ops
     │       ├── px6-ops
     │       ├── px7-ops
     │       └── px8-ops
     │
     │
     └── data
         └── ddsr.20190804  (sarra /apps/sarra/public_data/20190804 *)


The files found in the tools directory can be taken from the
sarracenia depot on github under ~/sarracania/tools. (If not in the master
they would be found in branch issue199)

For files found in the plugins directory directory can be taken from the 
sarracenia depot on github under ~/sarracania/sarra/plugins. (If not in the
master they would be found in branch issue199)

The config directory is just a straight copy of all the configs 
for each of the clusters... and here sr_sarra means the sarra portion
of pxatx.

For the logs and the data, one would think to have a whole day and so
I would always aim at getting all of "yesterday".  

The creation of data file (ddsr.20190804) was done as follow::

     ssh sarra@data-lb-ops1 '. ./.bash_profile; cd ~/master/saa; srl "cd /apps/sarra/public_data; find 20190804 -type f"' >> ddsr.20190804

On the server where you would to the migration, you need sarracenia of course.
The fact that px1-ops was off the sarra cluster was an opportunity since it
provides the same environment as the targetted cluster. If one such node is
not available when you a migration to a cluster (in fact I would be tempted
to say any migration of any kinds) ... I recommand you to have this setup.

SUNDEW SENDER CONVERSION PROCESS
================================

I cannot say for sure that all my tools get everything straight.
Should you find better ways or modifications to do, dont hesitate.

For now, here is how I would proceed with the tools::

Under ~/convert, create your own working/migrating directory.
Go there. Pick one config that you would like to start working with.
(Perhaps to start, the senders with the smallest number of delivery
would be a good start... dont do them all, keep some for the other
team member to sharp their teeth too).

To get the first 20 smallest senders ... the easiest, over file size::

    ls -al ~/convert/log/sundew/px2-ops/tx* | \
       awk '{print $5 " " $9}'              | \
       sed 's/ .*\// /'                     | \
       sort -n                              | head -n20


To get ready, make sure that the plugins under ~/convert/plugins are
sarra-wise available::
 
     cp ~/convert/plugins/* ~/.config/sarra/plugins

Ok now, convert that sender... Here I suppose as in the presentation
that it is accessdepot-iml.conf::

     # convert the sender place infos in directory ACCESSDEPOT_IML
     # The script will show an estimated of time to finish
     # that can be hours depending on the routing tables and sender configs

     do_this_sender.sh accessdepot-iml

     # access the resulting directory and have a look at the info
     # gathered by the script

     cd ACCESSDEPOT_IML
     vi INFO_accessdepot-iml

     # make sure the credential were extracted, ready for sarra
     ls credentials
     cat credentials

     # go check/edit/modify the configs and includes
     cd sender
     vi accessdepot-iml.conf

     # You think your sarra config/includes for this sender is ok
     # give it a try, run a whole day
     # *** CATCH in script sr_sender_one_day.sh
     # *** it appends to your sender config lines like
     # *** msg_file /local/home/sarra/convert/data/ddsr.20190804
     # *** THIS IS DATA DEPENDANT AND NEEDS TO BE TAKEN INTO ACCOUNT

     sr_sender_one_day.sh sender/accessdepot-iml.conf

     # check it out if this sender is done...
     # It will stop when all products of the data file are processed

     tail -f ~/.cache/sarra/log/sr_accessdepot-iml_01.log

     # When done compare the logs of the sundew sender
     # the sender's log have to be of the same date as the data product file

     compare.sh accessdepot-iml

     # IF the compare says the exact same number of products
     # and there are no product to be rejected or missing 
     # the sender is ready. 

     # If not... (and that is probably in most cases)
     # If there are no missing product... only some to be
     # rejected, would try restricting your accept/reject
     # and  you would loop doing the following until resolution
     #
     # 1- Fix the sender again
     # 2- Run through a whole day again
     # 3- check when finished
     # 4- compare
     #
     # a looping sequence like this :

     vi sender/accessdepot-iml.conf
     sr_sender_one_day.sh sender/accessdepot-iml.conf
     tail -f ~/.cache/sarra/log/sr_sender_accessdepot-iml_01.log
     compare.sh accessdepot-iml

     # missing products are more problematic
     # needs further investigation and perhaps
     # the addition of processes, or products to sarra
     

The presentation of this was done. And as I mentionned, I have not
done many of these sundew senders... only 2.  It was enough to figure
out that the work involved in migrating sundew senders was way too 
much if I wanted to finish the migration of pxatx' sundew pull processes
and so I opted to only migrate the sender's config into sarra and
deliver only the products I had migrated from pxatx... leaving the
whole suite of products to another sundew-sender migration project
to which I guess you are now responsible of some since you are 
reading this document... have fun  :-)





They are aware of nothing but the fact that they have to send the products
falling under their txq directories.

Having to decide which products fall under this directory is a very tricky
process. When a sender might have the option of accepting everything, one
have to refer to the routing tables to get a knowledge of what is



server for new products to be ingested in the sundew product flow. There are
two types namely *pull-file* and *pull-bulletin*. The difference between them 
is the way in which the product is processed/routed once downloaded.

**sarracenia** supports the same mechanism. **sr-poll** announces the
new products from the remote site and **sr-sarra** makes the products
available, downloading and annoncing the product locally.

It is fairly straight forward to convert a pull reveiver configuration file
to both an **sr-poll** and **sr-sarra** that play the same role.  There
is a new concept in *sarracenia* where the *source* of the product
needs to be specified in the path of the file tree. 

Fortunately, in the context of this *PXATX* conversion, in our sundew system,
the products are placed properly in a sarracenia tree and announced with amqp
under a defined *source* directory. We will use these sources informations.

This document is solely based on the PXATX experience and so one should take
the ideas and apply them to his/her context.


METHODOLOGY
===========

I did this document using a very simple *sundew* pull receiver to make
sure to put just the right amount of details.

First set up a conversion environment. Where sarracenia is downloaded,
make sure you can use the bash script *pull_2_pollsarra.sh* by updating 
your PATH environment variable. Use *git clone* to get an updated version
of *sarracenia* ( See `Dev <Dev.rst>`_ ).  Make sarracenia tools available
for direct shell commands::

    export PATH=...wherever.../sarracenia/tools:$PATH

Define a place where you want to convert pxatx pull::

    mkdir -p convert/pxatx
    cd convert/pxatx

Get all the sundew configurations of sundew pxatx::

    scp -r px@pxatx1-ops:/apps/px/etc .
   
Here we pick the configuration pull-BC-ENV_AQ-WAMR.conf, and proceed
to its converstion::
  
    cd etc/rx
    pull_2_pollsarra.sh pull-BC-ENV_AQ-WAMR.conf

The original file looks like this ::

    #
    # STATUS:       Operational
    #
    # DESCRIPTION:  pull Wamr data from British Columbia Ministry of Environment (BC MoE)
    #
    # CONTACT:      BC MoE contact:  AQHIDSI@Victoria1.gov.bc.ca
    #
    #

    type pull-file

    routemask        true
    routing_version  1
    routingTable     /apps/px/etc/pdsRouting.conf

    protocol ftp
    host     fake.host.gc.ca
    user     fakeuser
    password fakepass

    delete False
    timeout_get 90
    pull_sleep  180

    extension pull-BC-ENV_AQ-WAMR:GOV-BC:WAMR:3:ASCII

    directory /pub/outgoing/WAMR/EarthNetworks2/
    get .*.lsi

    # generate key with accept
    accept .*(lsi:pull-BC-ENV_AQ-WAMR:GOV-BC:WAMR:3:ASCII).*

The script created these files::

    ls credentials *BC-ENV_AQ-WAMR.conf
    credentials
    pull-BC-ENV_AQ-WAMR.conf
    poll_pull-BC-ENV_AQ-WAMR.conf
    sarra_get_pull-BC-ENV_AQ-WAMR.conf

My personal renaming convention is to rename the files ::

    mv poll_pull-BC-ENV_AQ-WAMR.conf BC_ENV_AQ_WAMR.conf
    mv sarra_get_pull-BC-ENV_AQ-WAMR.conf get_BC_ENV_AQ_WAMR.conf

So now we have the sr_poll BC_ENV_AQ_WAMR.conf and
the sr_sarra get_BC_ENV_AQ_WAMR.conf.


SR_POLL CONFIG
==============

The generated *sr_poll* config looks like this:
cat BC_ENV_AQ_WAMR.conf::

    #
    # STATUS:       Operational
    #
    # DESCRIPTION:  pull Wamr data from British Columbia Ministry of Environment (BC MoE)
    #
    # CONTACT:      BC MoE contact:  AQHIDSI@Victoria1.gov.bc.ca
    #
    #

    # on doit avoir le vip de ddsr.cmc.ec.gc.ca

    vip 142.135.12.146

    # post_broker is DDSR spread the poll messages

    post_broker amqp://SOURCE@ddsr.cmc.ec.gc.ca/
    post_exchange xs_SOURCE

    # options

    sleep 180
    timeout 90

    # to useless... left for backward compat
    to DDSR.CMC,DDI.CMC,CMC,SCIENCE,EDM

    # where to get the products

    destination ftp://fakeuser:fakepass@fakehost.gc.ca

    #where/how to get the products


    directory /pub/outgoing/WAMR/EarthNetworks2/
    get .*.lsi

    # generate key with accept
    accept .*(lsi:pull-BC-ENV_AQ-WAMR:GOV-BC:WAMR:3:ASCII).*

    # ==============================l
    # usually no accept... in sr_poll

The follows all the original option of the sundew pull as a reference.
To continue we need to know what product is ingested by that pull::

    ssh px@pxatx1-ops grep Ingested /apps/px/log/rx_pull-BC-ENV_AQ-WAMR.log

We find that one of the product "today" is
29_05_2019_04_25.lsi:pull-BC-ENV_AQ-WAMR:GOV-BC:WAMR:3:ASCII
Lets try to find it on pxatx sarracenia side how it is announced::

    ssh sarra@data-lb-ops1 'cd master/pxatx; srl grep 29_05_2019_04_25.lsi \*.log'

Just picking one of the notice leads us to this place ::

    20190529/PROVINCIAL/BC-ENV_AQ-WAMR/12/29_05_2019_04_25.lsi:pull-BC-ENV_AQ-WAMR:GOV-BC:WAMR:3:ASCII

By convention the directory after the date is the name of the SOURCE
for these products. So here PROVINCIAL is used as an amqp source user
for announcement and as one of the top directory leaf for its products
With theses informations we can finalized the **sr_poll** config ::

    vi BC_ENV_AQ_WAMR.conf

    change
    post_broker amqp://SOURCE@ddsr.cmc.ec.gc.ca
    post_exchange xs_SOURCE**

    for
    post_broker amqp://PROVINCIAL@ddsr.cmc.ec.gc.ca
    post_exchange xs_PROVINCIAL

The destination put by the script always contain all the credentials.
So we just edit to keep  protocol://user#host::

    change
    destination ftp://fakeuser:fakepass@fake.host.gc.ca

    for
    destination ftp://fakeuser@fake.host.gc.ca


Starting at comment  *# where to get the products*
down to the end of the file, the script attempted to reproduce
the *directory*, *get* and *accept/reject* options as in the original.
And finally it placed all the options of the original file as reference.
Make sure the sr_poll config is reflecting the original sundew one
Get rid of duplicated options, scrutening the rest of the file.
It is not our case here but if there are *reject* options in this config
keep them. For *accept* option, you dont really need them since option
*get* plays the same role::

    remove
    accept .*(lsi:pull-BC-ENV_AQ-WAMR:GOV-BC:WAMR:3:ASCII).*

After, change the *get* for *accept*.
So a cleaned version of the last lines of the *sr_poll* config would be::


    # where to get the products

    destination ftp://fakeuser@fake.host.gc.ca

    # product source directories

    directory /pub/outgoing/WAMR/EarthNetworks2/
    accept .*\.lsi


SR_SARRA CONFIG
===============

The generated *sr_sarra* config looks like this:
cat get_BC_ENV_AQ_WAMR.conf::

    #
    # STATUS:       Operational
    #
    # DESCRIPTION:  pull Wamr data from British Columbia Ministry of Environment (BC MoE)
    #
    # CONTACT:      BC MoE contact:  AQHIDSI@Victoria1.gov.bc.ca
    #
    #

    # source

    instances 1

    # receives messages from same DDSR queue spreads the messages

    broker amqp://feeder@ddsr.cmc.ec.gc.ca/
    exchange   xs_SOURCE

    # listen to spread the poll messages

    prefetch  10
    queue_name q_feeder.${PROGRAM}.${CONFIG}.SHARED

    source_from_exchange True

    # what to do with product

    mirror        False
    preserve_time False

    # MG CHECK DELETE
    #delete False
    delete False

    # directories

    directory ${PBD}/${YYYYMMDD}/${SOURCE}/--${0}-- to be determined ----
    accept    .*(something).*

    # destination

    post_broker   amqp://feeder@localhost/
    post_exchange xpublic
    post_base_url http://${HOSTNAME}
    post_base_dir /apps/sarra/public_data

Again we need to adjust to the SOURCE value which is PROVINCIAL::

    vi get_BC_ENV_AQ_WAMR.conf

    change
    exchange   xs_SOURCE

    for
    exchange   xs_PROVINCIAL

A special attention must be given to the *delete* option.
If the sundew pull configuration is deleting the products once
downloaded, to test our *sr_sarra* process we must not delete
products. By default, the script writes ::

    # MG CHECK DELETE
    #delete value
    delete False

Where *value* is the setting of the *delete* option in the sundew pull.
The *sr_sarra* configuration, when ready, can be tested without deletion.
When placed in operation, and the sundew pull withdrawn, if the *delete*
option should be *true*  just delete the 'delete False' and uncomment the
'delete True'.

To have the proper *directory*, *accept* settings (there might be more than
one), we want to search how the products are disposed on the sarracenia side.
Because it is sundew processes that mimic sarracenia we find theses informatios
in the sundew senders::

    % grep PROVINCIAL/BC-ENV_AQ-WAMR ../tx/*
    % tx/ddsr-PROVINCIAL.inc:directory //apps/sarra/public_data/${RYYYY}${RMM}${RDD}/PROVINCIAL/BC-ENV_AQ-WAMR/${RHH}

And looking for the conplete configuration setting for these products in
this include file we get::

    directory //apps/sarra/public_data/${RYYYY}${RMM}${RDD}/PROVINCIAL/BC-ENV_AQ-WAMR/${RHH}
    accept .*.lsi:pull-BC-ENV_AQ-WAMR:GOV-BC:WAMR:.*

The final changes in our *sr_poll* config is to reflect that finding::

    change**
    directory \${PBD}/\${YYYYMMDD}/\${SOURCE}/--\${0}-- to be determined ----
    accept    .*(something).*

    for
    directory ${PBD}/${YYYYMMDD}/${SOURCE}/BC-ENV_AQ-WAMR/${HH}
    accept .*\.lsi.*

And we are all set for testing.


TESTING
=======

We install *sr_poll* BC_ENV_AQ_WAM.conf and *sr_sarra* get_BC_ENV_AQ_WAM.conf 
on DDSR_DEV. (on ddsr_dev, there are various things to modify. Setting *xattr_disable true*, changing ddsr.cmc for ddsr_dev.cmc, in broker... *document_root* option in senders and perhaps more)

Leave the processes running and check the right disposal/announcement of the products.


RELATED CLIENTS
===============

There are five clusters to check in order to see where the products
are going. Because these products are regularly coming in, we can
check in the logs.

1- are the products delivered on pxatx sundew ::

    ssh px@px-lvs-ops1 '. .bash_profile; cd /apps/master/pxatx; pxl grep BC-ENV_AQ-WAMR [ft]x*.log' | sed 's/:.*$//' | sort -u
    # which gives
    --- pxatx-new
    tx_ddsr-PROVINCIAL.log
    tx_ddsr-notify-PROVINCIAL.log
    tx_dms-op1.log
    tx_dms-op2.log

The *ddsr* processes are used to put the products on the sarra side of pxatx.
So the only senders to migrate would be *dms-op1* and *dms-op2*. We should use
and include for specific products whenever it is suitable.

2- lets check on the sarracenia side of pxatx (senders should be migrated to
   ddsr when the migration will occur)::

    ssh sarra@data-lb-ops1 '. .bash_profile; cd master/pxatx; srl grep BC-ENV_AQ-WAMR *.log' | sed 's/log:.*$/log/' | sort -u
    pxatx1-ops: sr_shovel_copy-ddsr-PROVINCIAL_0001.log
    pxatx2-ops: sr_shovel_copy-ddsr-PROVINCIAL_0001.log

   Ok so the messages are shoveled to ddsr (the products stay on pxatx)


3- are the products flowing on sundew ::

    ssh px@px-lvs-ops1 '. .bash_profile; cd /apps/master/sundew; pxl grep BC-ENV_AQ-WAMR [rft]x*.log' | sed 's/:.*$//' | sort -u

    --- px1-ops
    --- px2-ops
    --- px3-ops
    --- px4-ops
    --- px5-ops
    --- px6-ops
    --- px7-ops
    --- px8-ops

4- are the products flowing on ddsr : (this is slowwww)::

    ssh sarra@data-lb-ops1 '. .bash_profile; cd master/sarra; srl grep BC-ENV_AQ-WAMR *.log' | sed 's/log:.*$/log/' | sort -u


5- are the products flowing on ddsr.science ::

    ssh sarra@data-lb-ops1 '. .bash_profile; cd master/ddsr_science; srl grep BC-ENV_AQ-WAMR \*.log' | sed 's/log:.*$/log/' | sort -u


MIGRATING FILTERS
=================

Will do another paper for sundew filters that become *sr_sarra*.


MIGRATING SENDER
================

Will do another paper on how to migrate senders.


SEE ALSO
--------

`sr_poll(1) <sr_poll.1.rst>`_ - post announcemensts of specific files.

`sr_sarra(8) <sr_sarra.8.rst>`_ - Subscribe, Acquire, and ReAdvertise tool.

`https://github.com/MetPX/ <https://github.com/MetPX/>`_ - sr_subscribe is a component of MetPX-Sarracenia, the AMQP based data pump.
