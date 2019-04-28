# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

from openstack import resource
from opentelekom import otc_resource


class CustomerMasterKey(otc_resource.OtcResource):
    resources_key = "keys"
    base_path = "/kms"

     # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True

    create_method = 'POST'

    # Properties
    #: key_alias: An alias name of the customer master key. It 
    #: must not exceed 255 bytes in length, according to the regex
    #: ^[a-zA-Z0-9:/_-]+{1,255}$
    key_alias = resource.Body("key_alias")
    #: key_description: CMK description (optional)
    key_description = resource.Body("key_desription")
    #: origin: where the key comes from. Values ["kms", "external"] (optional)
    origin = resource.Body("origin")
    #: sequence: an external, 36-byte serial number as additional reference
    sequence = resource.Body("sequence")

class CustomerMasterKeyAction(otc_resource.OtcResource):
    base_path = "/kms"

     # capabilities
    allow_create = True
    create_method = 'POST'

    # Properties
    #: key_id: The id of the resource to perform action on
    key_id = resource.Body("key_id")
    #: sequence: 36-byte serial number
    sequence = resource.Body("sequence")
    #---
    #: key_state: "2"=enabled, "3"=disabled, "4"=scheduled for deletion
    key_state = resource.Body("key_state")

class CustomerMasterKeyDelete(otc_resource.OtcResource):
    base_path = "/kms/schedule-key-deletion"

     # capabilities
    allow_create = True
    create_method = 'POST'

    # Properties
    #: key_id: The id of the resource to perform action on
    key_id = resource.Body("key_id")
    #: pending_days: delayed deletion for Cmk 7-1096 days
    pending_days = resource.Body("pending_days")
    #: sequence: 36-byte serial number
    sequence = resource.Body("sequence")
    #---
    #: key_state: "2"=enabled, "3"=disabled, "4"=scheduled for deletion
    key_state = resource.Body("key_state")

class CustomerMasterKeyList(otc_resource.OtcResource):
    base_path = "/kms/list-keys"

     # capabilities
    allow_create = True
    create_method = 'POST'

    # Properties
    #: limit: number of entries returned
    limit = resource.Body("limit")
    #: marker: marks starting location
    pending_days = resource.Body("pending_days")
    #: key_state: "2"=enabled, "3"=disabled, "4"=scheduled for deletion
    key_state = resource.Body("key_state")
    #: sequence: 36-byte serial number
    sequence = resource.Body("sequence")
