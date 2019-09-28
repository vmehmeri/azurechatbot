# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from connectivity_details import ConnectivityDetails
from vm_details import VmDetails

class Intent(Enum):
    NONE_INTENT = "NoneIntent"
    TEST_CONNECTIVITY = "TestConnectivity"
    GET_IP_ADDRESS = "GetIpAddress"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.TEST_CONNECTIVITY.value:
                print ("TEST_CONNECTIVITY")
                result = ConnectivityDetails()

                # We need to get the result from the LUIS JSON which at every level returns an array.
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "To", []
                )
                if len(to_entities) > 0:
                    if recognizer_result.entities.get("To", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.destination = to_entities[0]["text"].capitalize()
                    

                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "From", []
                )
                if len(from_entities) > 0:
                    if recognizer_result.entities.get("From", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.source = from_entities[0]["text"].capitalize()
                    

                proto_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Protocol", []
                )
                
                if len(proto_entities) > 0:
                    result.protocol = proto_entities[0]["text"].capitalize()
                
                port_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Port", []
                )
                if len(port_entities) > 0:
                    result.port = port_entities[0]["text"].capitalize()
                
            elif intent == Intent.GET_IP_ADDRESS.value:
                print ("GET_IP_ADDRESS")
                result = VmDetails()

                # We need to get the result from the LUIS JSON which at every level returns an array.
                print ("Recognizer_result", recognizer_result)
                vm_entity = recognizer_result.entities.get("$instance", {}).get(
                    "VM", []
                )
                if len(vm_entity) > 0:
                    # Get normalized name
                    result.name = recognizer_result.entities["VM"][0][0].capitalize()
                    print("Normalized VM name", result.name)
                

        except Exception as e:
            print(e)

        return intent, result
