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


