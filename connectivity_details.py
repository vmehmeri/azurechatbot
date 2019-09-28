# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List


class ConnectivityDetails:
    def __init__(
        self,
        source: str = None,
        destination: str = None,
        protocol: str = None,
        port: str = None,
    ):
        self.destination = destination
        self.source = source
        self.protocol = protocol
        self.port = port
