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
    related_instance = resource.Body("related_inastance", type=list)
    #: time_zone: timezone the nodes are running with
    time_zone = resource.Body("time_zone")
    #: replication_mode: mode for (standby) replication 
    #: MySQL: (asyn, semisync), PostgreSQL: (async, sync), SQLserver:(sync)
    replication_mode = resource.Body("replication_mode")

    def fetch(self, session, requires_id=True,
              base_path=None, error_message=None, **params):
        # RDS3 has no dedicated GET Method, so we have to use the list query with id
        result = list(DB.list(session, base_path=base_path, id=self.id))
        return result[0] if ( len(result)>0 ) else None

    def create(self, session, prepend_key=False, base_path=None):
        # disable resource_key prepend, and fake an initial status for wait
        res = super().create(session, prepend_key, base_path)
        res.status = "BUILD"
        return res