#!/bin/env python
#
# Description:
#   This tool displays the status of the glideinWMS pool
#   in a XML format
#
# Arguments:
#   [-pool collector_node] [-condor-stats 1|0] [-internals 1|0]
#
# Author:
#   Igor Sfiligoi (May 9th 2007)
#

import string
import os.path
import sys
sys.path.append(os.path.join(sys.path[0],"../factory"))
sys.path.append(os.path.join(sys.path[0],"../frontend"))
sys.path.append(os.path.join(sys.path[0],"../lib"))

import glideFactoryInterface
import glideinFrontendInterface
import xmlFormat

pool_name=None
remove_condor_stats=True
remove_internals=True

# parse arguments
alen=len(sys.argv)
i=1
while (i<alen):
    ael=sys.argv[i]
    if ael=='-pool':
        i=i+1
        pool_name=sys.argv[i]
    elif ael=='-condor-stats':
        i=i+1
        remove_condor_stats=not int(sys.argv[i])
    elif ael=='-internals':
        i=i+1
        remove_internals=not int(sys.argv[i])
    else:
        raise RuntimeError,"Unknown option '%s'"%ael
    i=i+1

# get data
glideins_obj=glideinFrontendInterface.findGlideins(pool_name)
clientsmon_obj=glideinFrontendInterface.findGlideinClientMonitoring(pool_name,None)

# extract data
glideins=glideins_obj.keys()
for glidein in glideins:
    glidein_el=glideins_obj[glidein]

    # Remove diagnostics attributes, if needed
    if remove_condor_stats:
        del glidein_el['attrs']['LastHeardFrom']

    #rename params into default_params
    glidein_el['default_params']=glidein_el['params']
    del glidein_el['params']

    if remove_internals:
        for attr in ('EntryName','GlideinName','FactoryName'):
            del glidein_el['attrs'][attr]
        
    entry_name,glidein_name,factory_name=string.split(glidein,"@")

    clients_obj=glideFactoryInterface.findWork(factory_name,glidein_name,entry_name)
    glidein_el['clients']=clients_obj
    clients=clients_obj.keys()
    for client in clients:
        if remove_internals:
            del clients_obj[client]['internals']
        
        # rename monitor into client_monitor
        clients_obj[client]['client_monitor']=clients_obj[client]['monitor']
        del clients_obj[client]['monitor']
        # add factory monitor
        if clientsmon_obj.has_key(client):
            clients_obj[client]['factory_monitor']=clientsmon_obj[client]['monitor']

        for pd_key in clients_obj[client]["params_decrypted"].keys():
            if clients_obj[client]["params_decrypted"][pd_key]==None:
                clients_obj[client]["params_decrypted"][pd_key]="ENCRYPTED"


#print data
sub_dict={'clients':{'dict_name':'clients','el_name':'client','subtypes_params':{'class':{}}}}
print xmlFormat.dict2string(glideins_obj,'glideinWMS','factory',
                            subtypes_params={'class':{'dicts_params':sub_dict}})

