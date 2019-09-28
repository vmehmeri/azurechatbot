# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog


class ConnectivityCheckDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(ConnectivityCheckDialog, self).__init__(dialog_id or ConnectivityCheckDialog.__name__)
        

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.destination_step,
                    self.source_step,
                    self.protocol_step,
                    self.port_step,
                    self.confirm_step,
                    self.result_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    """
    If a destination has not been provided, prompt for it.
    :param step_context:
    :return DialogTurnResult:
    """

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        connectivity_details = step_context.options

        if connectivity_details.destination is None:
            message_text = "To what destination?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(connectivity_details.destination)

    """
    If a source has not been provided, prompt for it.
    :param step_context:
    :return DialogTurnResult:
    """

    async def source_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        connectivity_details = step_context.options

        # Capture the response to the previous step's prompt
        connectivity_details.destination = step_context.result
        if connectivity_details.source is None:
            message_text = "From which source?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(connectivity_details.source)

    """
    If the connection protocol has not been provided, prompt for it.
    :param step_context:
    :return DialogTurnResult:
    """

    async def protocol_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        connectivity_details = step_context.options
        print(connectivity_details.protocol)
        # Capture the results of the previous step
        connectivity_details.source = step_context.result
        if not connectivity_details.protocol:
            message_text = "Which protocol (TCP/UDP/Any)?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(connectivity_details.protocol)

    """
    If the connection port has not been provided, prompt for it.
    :param step_context:
    :return DialogTurnResult:
    """

    async def port_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        connectivity_details = step_context.options

        # Capture the results of the previous step
        connectivity_details.protocol = step_context.result
        if not connectivity_details.port:
            message_text = "Which port number [1-65535]?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(connectivity_details.port)

    """
    Confirm the information the user has provided.
    :param step_context:
    :return DialogTurnResult:
    """

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        connectivity_details = step_context.options

        # Capture the results of the previous step
        connectivity_details.port = step_context.result
        message_text = (
            f"Please confirm, you want to check connectivity from { connectivity_details.source } to "
            f"{ connectivity_details.destination } on { connectivity_details.protocol.upper() } port { connectivity_details.port}?"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )
    
    """
    Obtain and Provide the result to the user.
    :param step_context:
    :return DialogTurnResult:
    """

    async def result_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result:
            connectivity_details = step_context.options
            result = step_context.result

        # TO DO: Use Network Watcher ipflowverify to check

        result_text = (
            f"The connectivity from {connectivity_details.source} to {connectivity_details.destination} " 
            f"on {connectivity_details.protocol} port {connectivity_details.port} is maybe ALLOWED, maybe DENIED"
        )
        result_message = MessageFactory.text(
            result_text, result_text, InputHints.ignoring_input
        )

        await step_context.context.send_activity(result_message)
        return await step_context.next(result)

    """
    Complete the interaction and end the dialog.
    :param step_context:
    :return DialogTurnResult:
    """

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        if step_context.result:
            connectivity_details = step_context.options
            return await step_context.end_dialog(connectivity_details)
        return await step_context.end_dialog()

    