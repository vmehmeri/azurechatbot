import json
from azure_resource_broker import AzureResourceBroker
from config import AzureConfig

vm_entity_sublist = []
for sub_name, sub_id in AzureConfig.AZURE_SUBSCRIPTION_ID_MAP.items():
    print ("Fetching VMs from subscription", sub_name)
    broker = AzureResourceBroker(sub_id)
    broker.load_resources()

    vm_names = broker.get_virtual_machine_names()
    for vm_name in vm_names:
        vm_entity_sublist.append({
            "canonicalForm": vm_name,
            "list": []
        })

with open("vm_entity_sublist.json", 'w') as f:
    json.dump(vm_entity_sublist, f, indent=4)
