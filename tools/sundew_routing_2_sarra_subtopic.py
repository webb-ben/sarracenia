#!/usr/bin/python3

# sundew_routing_2_sarra_subtopic.py 
# arguments pxtable1.conf ... pxtableN.conf 1day_brokerfilelist sender.conf
#
# This program reads all routing entries related to sender.conf
# Than it reads in



import os,re,sys

config=sys.argv[-1]
client=os.path.basename(config)
client=client.replace('.conf','')

# find routing table pattern match for that client

client_search_list=[]
client_search_list.append(client)

routing_pattern_list=[]

for table in sys.argv[1:-2]:
    tablefile=open(table,'r')
    for line in tablefile:
        for client in client_search_list:
            try :
                    words=line.split()
                    product_client_list=words[2].split(',')

                    if client in product_client_list:
                       if words[0] == 'clientAlias' and not words[1] in client_search_list:
                          client_search_list.append(words[1])
                          continue
                       if words[0] == 'key' :
                          pattern = '.*' + words[1].replace('_','.*') + '.*'
                          routing_pattern_list.append(re.compile(pattern))
            except: continue
    tablefile.close()

## load accept reject from client

config_pattern_list=[]
config_pattern_bool=[]

configfile=open(config,'r')
for line in configfile:
    words = line.split()
    try:
        if words[0] in ['accept','reject']:
           config_pattern_list.append( re.compile(words[1]) )
           config_pattern_bool.append( words[0] == 'accept' )
    except:pass

configfile.close()

# check in one day of ddi products

subtopic_list=[]

productfile=open(sys.argv[-2],'r')
for product in productfile:

    # check routingtable match

    rejected=False
    for rpattern in routing_pattern_list :

        # routing table no match...
        if not rpattern.match(product): continue

        # ok matched routing table ... see how it goes with config

        for i,cpattern in enumerate(config_pattern_list):

            # product not configured
            if not cpattern.match(product) : continue

            # product rejected
            if not config_pattern_bool[i] :
               rejected = True
               break

            # product process by this config so get its subtopic
            dirname = os.path.dirname(product)
            subtopic = dirname.replace('/','.')
            if  not subtopic in subtopic_list :
                subtopic_list.append(subtopic)
                print("subtopic",subtopic)

        # product matched but was rejected
        if rejected : break

#
productfile.close()
