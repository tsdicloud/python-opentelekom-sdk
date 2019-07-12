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
from openstack import utils
from openstack import exceptions

from opentelekom import otc_resource

class DB(otc_resource.OtcResource, otc_resource.TagMixin):
    resources_key = "instances"
    resource_key = "instance" # top structure 
    base_path = "/instances"

     # capabilities
    allow_create = True
    allow_commit = False # !no update
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'

    _query_mapping = resource.QueryParameters(
        "id", 
        "name", 
        "type",
        "datastore_type",
        "vpc_id",
        "subnet_id",
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #--- create properties
    #: name: name of the db instance
    name = resource.Body("name")
    #: datastore: details about the  datastore
    datastore = resource.Body("datastore", type=dict)
    #: ha: high availability information (optional)
    ha = resource.Body("ha", type=dict)
    #: configuration_id: id of an adapted parameter group (optional)
    configuration_id = resource.Body("configuration_id")
    #: port: database port (optional, otherwide DB default port used)
    #: MySQL:default=3306, PostgreSQL: default=5432, SQLserver:default=1433
    port = resource.Body("port", type=int)
    #: password: DB password to use
    password = resource.Body("password")
    #: backup_strategy: the backup policy (optional)
    backup_strategy = resource.Body("backup_strategy")
    #: disk_encryption_is: id of the CMK for DB encryption (optional)
    disk_encryption_id = resource.Body("disk_encryption_id")
    #: flavor_ref: id of the DB flavor
    flavor_ref = resource.Body("flavor_ref")
    #: volume: specification of the volumes use by the instances
    volume = resource.Body("volume", type=dict)
    #: region: the name of the region OR project where db is installed
    region = resource.Body("region")
    #: availability_zone: name of the primary AZ the DB is located
    #: for replication and ha, this is a comma-separated list of az names 
    #: as string, NOT as list! 
    availability_zone = resource.Body("availability_zone")
    #: vpc_id: vpc/router id where the database is located
    vpc_id = resource.Body("vpc_id")
    #: subnet_id: subnet id where the database is located
    subnet_id = resource.Body("subnet_id")
    #: security_group_id: Security group which secures this DB resource
    security_group_id = resource.Body("security_group_id")
    #: charge_info: alternative charging model to refer to (optional)
    #: at the moment, only pay-per-use is supported
    #:--- for read replica
    #: replica_of_id: the database to replicated (mandatory for read replicas)
    replica_of_id = resource.Body("replica_of_id")

    #--- get/list resource
    #: status: instance state
    status = resource.Body("status")
    #: private_ips: list of private access addresses
    private_ips = resource.Body("private_ips", type=list)
    #: public_ips: list of internet access addresses
    public_ips = resource.Body("public_ips", type=list)
    #: avtype: availability type (HA, Single, Replica)
    avtype = resource.Body("type")
    #: created: creation time as yyyy-mm-ddThh:mm:ssZ
    created = resource.Body("created")
    #: updated: last update time as yyyy-mm-ddThh:mm:ssZ
    updated = resource.Body("updated")
    #: switch_strategy: indicated the DB switchover strategy values=(reliability, availability)
    switch_strategy = resource.Body("switch_strategy")
    #: maintenance_window: the maintainance window time interval
    maintenance_window = resource.Body("maintenance_window")
    #: nodes: list of nodes belonging ti the DB cluster (primary/standby)
    nodes = resource.Body("nodes", type=list)
    #: related_instance: associated DB instances
    related_instance = resource.Body("related_instance", type=list)
    #: time_zone: timezone the nodes are running with
    time_zone = resource.Body("time_zone")
    #: replication_mode: mode for (standby) replication 
    #: MySQL: (asyn, semisync), PostgreSQL: (async, sync), SQLserver:(sync)
    replication_mode = resource.Body("replication_mode")
    #: job_id: id of a running job
    #: Could be used to wait for job finishing
    job_id = resource.Body("job_id")

    def _translate_response(self, response, has_body=None, error_message=None):
        """ Extend the default behaviour to add job_id from response top-level if available """
        resp = response.json()    
        if 'job_id' in resp:
            self._body['job_id'] = resp['job_id']
            self._body.clean()
        super()._translate_response(response, has_body=has_body, error_message=error_message)

    def fetch(self, session, requires_id=True,
              base_path=None, error_message=None, **params):
        """ RDS3 has no dedicated GET Method, so we have to use the list query with id """
        result = list(DB.list(session, base_path=base_path, id=self.id))
        if result:
            return result[0]
        else:
            raise exceptions.ResourceNotFound(details="RDS DB not found.", http_status=404)


    def create(self, session, prepend_key=False, base_path=None):
        # disable resource_key prepend as default setting, and fake an initial status for wait
        res = super().create(session, prepend_key, base_path)
        res.status = "BUILD"
        return res


class DBJob(otc_resource.OtcResource):
    """ Job status for RDS v3 operations """
    resource_key="job"

     # capabilities
    allow_create = False
    allow_commit = False # !no update
    allow_list = False
    allow_fetch = True
    allow_delete = False

    _query_mapping = resource.QueryParameters("id")

    #--- get/fetch fields
    #: name: Name of the task
    name = resource.Body('name')
    #: name: Name of the task
    name = resource.Body('name')
    #: status: Task status
    #: possible values are: Running, Completed, Failed
    status = resource.Body('status')
    #: created: timestamp of job creation, "yyyy-mm-ddThh:mm:ssZ" format
    created = resource.Body('created')
    #: process: progess indication
    process = resource.Body('process')
    #: instance: details about the targetted instances
    instance = resource.Body('instance', type=dict)
    #: entities: details about the job, depending on job type
    entities = resource.Body('entities', type=dict)

    def fetch(self, session, requires_id=False,
              base_path=None, error_message=None, **params):
        base_path = "/jobs?id=%s" % self.id
        return super().fetch(session, requires_id, base_path, error_message, **params)
