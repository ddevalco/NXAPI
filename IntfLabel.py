# Author: Jamie Caesar
# Twitter: @j_cae
# 
# This script polls the device for the needed information and:
# 1) Labels interfaces based on CDP information.
# 2) Labels port-channels based on member port CDP information
#
# TO DO in a future version:
# 3) Labels ports and port-channels connected to Fabric Extenders  
#

from argparse import ArgumentParser
from nxapi_base import NXOS, short_intf, short_name


def makeDescriptions(cdp, pc):
    neighbor_list = cdp["TABLE_cdp_neighbor_detail_info"]["ROW_cdp_neighbor_detail_info"]
    pc_list = pc["TABLE_channel"]["ROW_channel"]
    if type(pc_list) == dict:
        pc_list = [pc_list]
    desc_list = []
    for neighbor in neighbor_list:
        desc_list.append('int {} ;description {}:{}'.format(neighbor["intf_id"], 
            short_name(neighbor["device_id"]), short_intf(neighbor["port_id"])))
    for group in pc_list:
        interface = group["port-channel"]
        remote = None
        members = group["TABLE_member"]["ROW_member"]
        for member in members:
            for neighbor in neighbor_list:
                if member["port"] == neighbor["intf_id"]:
                    if not remote:
                        remote = short_name(neighbor["device_id"])
                    elif remote != short_name(neighbor["device_id"]):
                        remote = 'vPC:' + remote + ', ' + short_name(neighbor["device_id"])
        if remote:
            desc_list.append('int {} ;description {}'.format(interface, remote))
    return desc_list


def main(args):
    n9k = NXOS(args.mgmt_ip)
    n9k.PromptCreds()
    print "Gathering data."
    cdp_data = n9k.cli_show('show cdp neighbor detail')
    pc_data = n9k.cli_show('show port-channel summary')
    desc_cmds = makeDescriptions(cdp_data, pc_data)
    n9k.cli_conf(desc_cmds)
    print "Descriptions Complete."


if __name__ == '__main__':
    parser = ArgumentParser(description = "Enter the IP address of the device to connect with.")
    parser.add_argument("mgmt_ip", help="The management IP address of the NXAPI device you are "
        "connecting to.")
    args = parser.parse_args()
    main(args)