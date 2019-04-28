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


class Queue(otc_resource.OtcResource):
    resources_key = "queues"
    base_path = "/queues"

    _query_mapping = resource.QueryParameters("include_deadletter", "include_messages_num")
    # FIXME: Get does only have one query parameter
    #_query_mapping = resource.QueryParameters("include_deadletter")

     # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'

    # Properties
    #: Name of the queue. The name is the unique identity of a queue. It
    #: must not exceed 64 bytes in length, and it is limited to US-ASCII
    #: letters, digits, underscores, and hyphens.
    name = resource.Body("name", alternate_id=True)
    #: type of the queue; one of NORMAL, FIFO, KAFKA_HA, KAFKA_HT
    queue_mode = resource.Body("queue_mode",)
    #: Description of the queue.
    description = resource.Body("description")
    #: enable or disable deadletter_queue 
    #: values are enable or disable
    #: only valid for NORMAL or FIFO mode
    redrive_policy = resource.Body("redrive_policy")
    #: maximum number of messages failed to consume
    #: only valid if redrive_policy=enable
    #: Value range 1-100
    max_consume_count = resource.Body("max_consume_count", type=int)
    #: time to store messages
    #: only valid for mode KAFKA_HA or KAFKA_HT
    #: value range 1-72
    retention_hours = resource.Body("retention_hours", type=int)