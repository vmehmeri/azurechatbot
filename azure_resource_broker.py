from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.common.client_factory import get_client_from_cli_profile
from functools import lru_cache
from config import AzureConfig
from typing import Dict
import json
import os


class AzureResourceBroker:

    def __init__(self, subscription_id):
        self.resource_client = get_client_from_cli_profile(ResourceManagementClient,subscription_id=subscription_id)
        self.network_client = get_client_from_cli_profile(NetworkManagementClient,subscription_id=subscription_id)
        self.compute_client = get_client_from_cli_profile(ComputeManagementClient,subscription_id=subscription_id)
        self.resource_groups = []
        self.resources = {}
        self.resource_cache_filepath = f"cache/{subscription_id}.resources.json"

    @lru_cache(maxsize=32)
    def load_resources(self):

        print ("AZURE BROKER: Fetching resources from Azure Resource Manager...")
        for resource_group in self.resource_client.resource_groups.list():
            self.resource_groups.append(resource_group.name)

        for rg in self.resource_groups:
            self.resources[rg] = []
            for resource in self.resource_client.resources.list_by_resource_group(rg):
                self.resources[rg].append(resource.as_dict())
        

    def load_resources_from_file(self):
        with open(self.resource_cache_filepath, 'r') as f:
            self.resources = json.load(f)
        
        for resource_group in self.resources.keys():
            self.resource_groups.append(resource_group)


    @lru_cache(maxsize=32)
    def get_virtual_machine_ip_addresses(self, virtual_machine_name):
        if not self.resources:
            self.load_resources()
        
        ips = []
        for rg in self.resource_groups:
            for resource in self.resources[rg]:
                if resource['type'] == "Microsoft.Compute/virtualMachines" and resource['name'].lower() == virtual_machine_name.lower():
                    vm_nics = self.compute_client.virtual_machines.get(rg,resource['name']).network_profile.network_interfaces
                    for vm_nic in vm_nics:
                        vm_nic_id = vm_nic.id
                        vm_nic_name = vm_nic_id.split('/')[-1]
                        for ip_config in self.network_client.network_interfaces.get(rg, vm_nic_name).ip_configurations:
                            ips.append(ip_config.private_ip_address)
                        
                   
        return ips

    @lru_cache(maxsize=32)
    def get_virtual_machine_names(self):
        if not self.resources:
            self.load_resources()
        #print("Looking for Virtual Machines...")
        vm_names = []
        for rg in self.resource_groups:
            for resource in self.resources[rg]:
                if resource['type'] == "Microsoft.Compute/virtualMachines":
                    vm_name = resource['name']
                    vm_names.append(vm_name)

        #print(f"Found {len(vm_names)} VMs")
        return vm_names


#if __name__ == '__main__':
#    print ("Starting...")
#
#    broker = AzureResourceBroker()
#
#    broker.load_resources()
#    #res_dict = arm.resources

#    print(broker.get_virtual_machine_ip_addresses("vAEMTPLDE2AP1"))

    


## arm.network_client.network_security_groups.get('GOE-HUB-NPR-SEC-rg','GOE-NPR-ManagementSubnet-nsg').as_dict().security_rules

