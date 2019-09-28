# AzureChatbot

An implementation of Bot Framework v4 with Python.

This bot has been created using [Bot Framework](https://dev.botframework.com), it is a simple Azure chatbot for asking questions about IaaS Virtual Machines. Example of questions/utterances are:

- What is the Ip address of 'VM_Name'?
- I would like to check an ip address  (Chatbot prompts for VM name)
- Can you test connectivity between VM1 and VM2 on TCP port 22? (Uses Network Watcher)
- Check connectivity to VM2 (Chatbot prompts for all other missing information needed)
- Can you test connectivity (Chatbot prompts for: source, destination, protocol, tcp, port)
- ...

Some other capabilities are:

- Handle user interruptions for such things as `Help` or `Cancel`
- Prompt for and validate requests for information from the user

## Prerequisites

This chatbot **requires** prerequisites in order to run.

- Python 3.7
- Run `pip install -r requirements.txt` to install all dependencies
- Run `az login` (this bot uses Azure CLI client profile which requires that your local user be logged in via Azure CLI. You can also modify the code to use a Service Principal instead)

This bot uses [LUIS](https://www.luis.ai), an AI based cognitive service, to implement language understanding. See below for how to create a trial Luis Application (quick setup, no cost)

### Create a LUIS Application to enable language understanding

LUIS language model setup, training, and application configuration steps can be found [here](https://docs.microsoft.com/azure/bot-service/bot-builder-howto-v4-luis?view=azure-bot-service-4.0&tabs=cs).

If you wish to create a LUIS application via the CLI, these steps can be found in the [README-LUIS.md](README-LUIS.md).

#### Import cognitive model to LUIS Application
The file `cognitiveModels/AzureChatBot.json` contains a sample model that you can import into your LUIS Application so that the Entities, Intents and Utterances will be setup and you can start using the bot immediately. Note that the model requires that all your Azure Virtual Machines be listed, you can either manually edit the file or use the helper python script generate_vm_entity_sublist.py to generate a JSON snippet in the right format with all your VMs (make sure you add your subscription information in `config.py` first).

## Running the sample
- Update LuisAppId, LuisAPIKey and LuisAPIHostName in `config.py` with the information retrieved from the [LUIS portal](https://www.luis.ai)
- Update `config.py` with your Azure Subscription(s) information. More than one subscription is supported
- Run `python app.py`
- Alternatively to the last command, you can set the file in an environment variable with `set FLASK_APP=app.py` in windows (`export FLASK_APP=app.py` in mac/linux) and then run `flask run --host=127.0.0.1 --port=3978`


## Testing the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the Bot Framework Emulator version 4.3.0 or greater from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- Enter a Bot URL of `http://localhost:3978/api/messages`

### Testing Azure connection
Run `python test_azure_resource_broker.py` to test your Azure CLI connection by fetching a list of all your virtual machines
