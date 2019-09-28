from azure_resource_broker import AzureResourceBroker
from config import AzureConfig

if __name__ == '__main__':
    print ("Starting...")
    config = AzureConfig()

    for sub_name, sub_id in config.AZURE_SUBSCRIPTION_ID_MAP.items():
        broker = AzureResourceBroker(sub_id)
        print("Loading resources from subscription", sub_name)
        broker.load_resources()
        vms = broker.get_virtual_machine_names()
        print("Found VMs:")
        for vm in vms:
            print(vm)

    


