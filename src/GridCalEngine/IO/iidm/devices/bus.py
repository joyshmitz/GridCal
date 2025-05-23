# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
from GridCalEngine.IO.iidm.devices.rte_object import RteObject


class Bus(RteObject):
    def __init__(self, id):
        super().__init__("Bus")
        self.id = id

        self.register_property("id", "bus:id", str, description="Bus ID")
