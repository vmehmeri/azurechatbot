# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List


class VmDetails:
    def __init__(
        self,
        name: str = None,
        subscription: str = None,
    ):
        self.name = name
        self.subscription = subscription
