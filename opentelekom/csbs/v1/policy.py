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

class PolicyParametersSpec(otc_resource.OtcSubResource):
    """ At the moment an empty dict which must be given """
    # Properties
    #: common: Name of the sub dict for common params
    common = resource.Body("common", type=dict)


class ResourceSpec(otc_resource.OtcSubResource):
    # Properties
    #: id: id of the resource, mandatory here.
    #: os_type: type of the resource, at the moment only
    #: OS::Nova::Server, mandatory
    type = resource.Body("type", default="OS::Nova::Server")
    #: name: name of the object in backup, mandatory
    name = resource.Body("name")
    #: extra_info: name,value pairs for future use
    extra_info = resource.Body("extra_info", type=dict) 


class OperationDefinitionSpec(otc_resource.OtcSubResource):
    # Properties
    #: max_backup: number of backups to keep, -1 for no limit, charcters!
    max_backups = resource.Body("max_backups", type=int) # TODO: marked as string in docu!
    #: retention_duration_days: days to keep a backup, -1 for no limit, characters! 
    retention_duration_days = resource.Body("retention_duration_days", type=int) # TODO: marked as string in docu!
    #: permanent: "true" if backups should be permanently kept for retain, 
    #: bool as characters!
    permanent= resource.Body("permanent")
    #: -- get/fetch/update
    #: plan_id: id of the backup plan
    plan_id = resource.Body("plan_id")
    #: provider_id: the backup provider used, at the moment only a fixed value
    provider_id = resource.Body("provider_id")


class TriggerPropertiesSpec(otc_resource.OtcSubResource):
    # Properties
    #: pattern: a schedule pattern according to iCalendar RFC 2445
    #: but supports only FREQ, BYDAY, BYHOUR, and BYMINUTE, max. 10240 chars
    #: (see OTC API specification for more details)
    pattern = resource.Body("pattern")


class TriggerSpec(otc_resource.OtcSubResource):
    # Properties
    #: properties: trigger sub-structure to fill
    properties = resource.Body("properties", type=TriggerPropertiesSpec)


class ScheduledOperationSpec(otc_resource.OtcSubResource):
    # Properties
    #: description: some textual comments for the backup
    description = resource.Body("description")
    #: enabled: enable/disable an operation
    enabled = resource.Body("enabled", type=bool)
    #: name: a name for the schedule entry
    name = resource.Body("name") 
    #: operation_type: type of operation; only vaue "backup" at the moment
    operation_type = resource.Body("operation_type")
    #: operation_definition: handling strategy of the backups
    operation_definition = resource.Body("operation_definition", type=OperationDefinitionSpec)
    #: trigger: scheduling trigger specification
    trigger = resource.Body("trigger", type=TriggerSpec)
    #: -- get/fetch


class Policy(otc_resource.OtcResource, otc_resource.TagMixin):
    resources_key = "policies"
    resource_key = "policy"
    base_path = "/policies"

     # capabilities
    allow_create = True
    allow_commit = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'

    _query_mapping = resource.QueryParameters(
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #: name: Name of the backup policy.
    #: must not exceed 255 characters in length, and it is limited to US-ASCII
    #: letters, digits, underscores, and hyphens.
    name = resource.Body("name")
    #: description: some descriptive text up to 255 characters, no <, >
    description = resource.Body("description")
    #: parameters: set of general policy parameters
    parameters = resource.Body("parameters", type=PolicyParametersSpec)
    #: provider_id: preparation for multiple provider support, 
    #: at the moment fixed value default fc4d5750-22e7-4798-8a46-f48f62c4c1d
    provider_id = resource.Body("provider_id")
    #: resources: list of resources to backup; must be given, but could be empty
    resources = resource.Body("resources", type=list, list_type=ResourceSpec)
    #: scheduled_operations: specification of a backup schedule plan
    #: requires at least one entry in list
    scheduled_operations = resource.Body("scheduled_operations", type=list, list_type=ScheduledOperationSpec)
    # TODO: special, direct tags added as properties here

    #: -- get/fetch
    #: status: cluster status
    status = resource.Body("status")
    #: created: creation timestamp
    created = resource.Body("created_at")



    def _prepare_request(self, requires_id=True, prepend_key=True,
                         base_path=None):
        '''This is a workaround for the non-properly working default value of
           the resource framework see openstacksdk.compute.v2.server.'''
        self.provider_id = "fc4d5750-22e7-4798-8a46-f48f62c4c1da"
    
        return super()._prepare_request(requires_id=requires_id,
            prepend_key=prepend_key, base_path=base_path)