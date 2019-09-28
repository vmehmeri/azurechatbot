# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.dialogs.choices import Choice, ChoiceFactory, ListStyle
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from azure_resource_broker import AzureResourceBroker
from config import AzureConfig

class IpCheckDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(IpCheckDialog, self).__init__(dialog_id or IpCheckDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.vm_step,
                    self.subscription_step,
                    self.result_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    """
    If a VM has not been provided, prompt for it.
    :param step_context:
    :return DialogTurnResult:
    """

    async def vm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        vm_details = step_context.options

        if vm_details.name is None:
            message_text = "Of which VM?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )


        return await step_context.next(vm_details.name)

    """
    Ask for the Azure Subscription.
    :param step_context:
    :return DialogTurnResult:
    """

    async def subscription_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result:
            vm_details = step_context.options
            vm_details.name = step_context.result

        if vm_details.subscription is None:
            # Ask for the Subscription
            list_of_choices = [Choice(value=v) for v in AzureConfig.AZURE_SUBSCRIPTION_ID_MAP.keys()]

            # If there's only one subscription, no need to ask
            if len(list_of_choices) == 1:
                subscription_id = AzureConfig.AZURE_SUBSCRIPTION_ID_MAP.values()[0]
                vm_details.subscription = subscription_id
                return step_context.next(vm_details.subscription)

            choice_message_text = "In which subscription?"
            prompt_message = MessageFactory.text(
                choice_message_text, choice_message_text, InputHints.expecting_input
            )

            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(prompt=prompt_message, choices=list_of_choices, style=ListStyle.auto)
            )

        return await step_context.next(vm_details.subscription)

    """
    Obtain and Provide the result to the user.
    :param step_context:
    :return DialogTurnResult:
    """

    async def result_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result:
            vm_details = step_context.options
            vm_subscription = step_context.result.value
            vm_details.subscription = vm_subscription

        vm_name = vm_details.name
        subscription_id = AzureConfig.AZURE_SUBSCRIPTION_ID_MAP[vm_subscription]

        check_text = f"Let me check..."
        check_message = MessageFactory.text(check_text, check_text, InputHints.ignoring_input)
        await step_context.context.send_activity(check_message)
        azure_resource_broker = AzureResourceBroker(subscription_id)
        vm_ips = azure_resource_broker.get_virtual_machine_ip_addresses(vm_name)
        if vm_ips is None or len(vm_ips) == 0:
            err_text = f"Sorry, I couldn't find the IP address of {vm_name}."
            err_message = MessageFactory.text(err_text, err_text, InputHints.ignoring_input)
            await step_context.context.send_activity(err_message)
        else:
            if len(vm_ips) == 1:
                ip_text = f"The IP address of {vm_name.lower()} is {vm_ips[0]}"
            else:
                ip_text = f"The VM {vm_name.lower()} has the following ip addresses: {', '.join(vm_ips)}"

            ip_message = MessageFactory.text(ip_text, ip_text, InputHints.ignoring_input)
            await step_context.context.send_activity(ip_message)

        return await step_context.next(vm_name)

    """
    Complete the interaction and end the dialog.
    :param step_context:
    :return DialogTurnResult:
    """

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog()

    