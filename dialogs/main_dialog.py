# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import InputHints

from .connectivity_check_dialog import ConnectivityCheckDialog
from .ip_check_dialog import IpCheckDialog
from connectivity_details import ConnectivityDetails
from vm_details import VmDetails
from connectivity_check_recognizer import ConnectivityCheckRecognizer
from helpers.luis_helper import LuisHelper, Intent


class MainDialog(ComponentDialog):
    def __init__(
        self, luis_recognizer: ConnectivityCheckRecognizer, connectivity_check_dialog: ConnectivityCheckDialog, ip_check_dialog: IpCheckDialog
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self._luis_recognizer = luis_recognizer
        self._connectivity_check_dialog_id = connectivity_check_dialog.id
        self._ip_check_dialog_id = ip_check_dialog.id
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(connectivity_check_dialog)
        self.add_dialog(ip_check_dialog)
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.intro_step, self.act_step, self.final_step]
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)
        message_text = (
            str(step_context.options)
            if step_context.options
            else "What can I help you with today?"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            print("_luis_recognizer not configured!")
            # LUIS is not configured, we just run the ConnectivityDialog path with an empty ConnectivityDetails instance.
            return await step_context.begin_dialog(
                self._connectivity_check_dialog_id, ConnectivityDetails()
            )

        # Call LUIS and gather any potential connectivity details. 
        # (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )

   
        if intent == Intent.TEST_CONNECTIVITY.value:
            # Run the ConnectivityCheckDialog giving it whatever details we have from the LUIS call.
            return await step_context.begin_dialog(self._connectivity_check_dialog_id, luis_result)
        
        elif intent == Intent.GET_IP_ADDRESS.value:
            return await step_context.begin_dialog(self._ip_check_dialog_id, luis_result)
            
            #print("Checking VM Ip...")
            #check_text = f"Let me check..."
            #check_message = MessageFactory.text(check_text, check_text, InputHints.ignoring_input)
            #await step_context.context.send_activity(check_message)

         
            #vm_ips = self.azure_resource_broker.get_virtual_machine_ip_addresses(vm_name)
            #if vm_ips is None or len(vm_ips) == 0:
            #    err_text = f"Sorry, I couldn't find the IP address of {vm_name}. Are you logged in to the right subscription?"
            #    err_message = MessageFactory.text(err_text, err_text, InputHints.ignoring_input)
            #    await step_context.context.send_activity(err_message)
            #else:
            #    if len(vm_ips) == 1:
            #        ip_text = f"The IP address of {vm_name.lower()} is {vm_ips[0]}"
            #    else:
            #        ip_text = f"The VM {vm_name.lower()} has the following ip addresses: {', '.join(vm_ips)}"
            #
            #    ip_message = MessageFactory.text(ip_text, ip_text, InputHints.ignoring_input)
            #    await step_context.context.send_activity(ip_message)
          


        else:
            didnt_understand_text = (
                "Sorry, I didn't get that."
            )
            didnt_understand_message = MessageFactory.text(
                didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(didnt_understand_message)

        return await step_context.next(None)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        prompt_message = "What else can I do for you?"
        return await step_context.replace_dialog(self.id, prompt_message)

   
