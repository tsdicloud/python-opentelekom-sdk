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

import six
import pdb

from openstack import connection
from openstack import service_description

from openstack import exceptions


def connect_from_ansible(module):
    """ The method contains also a temporary fix for rdsv3 endpoint """
    # FIXME
    cloud_config = module.params.pop('cloud', None)
    try:
        if isinstance(cloud_config, dict):
            fail_message = (
                "A cloud config dict was provided to the cloud parameter"
                " but also a value was provided for {param}. If a cloud"
                " config dict is provided, {param} should be"
                " excluded.")
            for param in (
                    'auth', 'region_name', 'validate_certs',
                    'ca_cert', 'client_key', 'api_timeout', 'auth_type'):
                if module.params[param] is not None:
                    module.fail_json(msg=fail_message.format(param=param))
            # For 'interface' parameter, fail if we receive a non-default value
            if module.params['interface'] != 'public':
                module.fail_json(msg=fail_message.format(param='interface'))
            cloud_conn = Connection(**cloud_config)
        else:
            auth_dict = {
                'cloud': cloud_config,
                'auth_type': module.params['auth_type'],
                'auth': module.params['auth'],
                'region_name': module.params['region_name'],
                'verify': module.params.get('verify', module.params.get('validate_certs')),
                'cacert': module.params['cacert'],
                'key': module.params.get('key', module.params.get('client_key')),
                'api_timeout': module.params['api_timeout'],
                'interface': module.params['interface'],
            }    
            cloud_conn = Connection(**auth_dict)

        return cloud_conn

    except exceptions.SDKException as e:
        # Probably a cloud configuration/login error
        module.fail_json(msg=str(e))


def _patch_config(prop, value, config, **params):
    if config:
        if prop not in config.config:
            config.config[prop] = value
    else:
        if prop not in params:
            params[prop] = value


class Connection(connection.Connection):
    """ This class intercepts the openstack connection and 
    injects some (still needed) workarounds for endpoints and version detection
    for Open Telekom Cloud """


    def __init__(self, config=None, **params):

        # FIXME: Endpoint override workarounds: add here   
        #_patch_config(config, 'rdsv3_endpoint_override',
        #    "https://rds.eu-de.otc.t-systems.com/v3/%(project_id)s", **params)
        _patch_config('ccev2.0_endpoint_override',
            "https://cce.eu-de.otc.t-systems.com/api/v3/projects/%(project_id)s", 
            config, **params)

        # FIXME: Version detection workarounds: add here
        _patch_config('vpc_api_version', "1", config, **params)
        _patch_config('vpc2.0_api_version', "2", config, **params)
        _patch_config('ccev2.0_api_version', "3", config, **params)


        # hand over patched config to openstack.Connection
        super().__init__(config=config, **params)


    # FIXME: remove if registration bug of (at least since) 0.27.0 is fixed
    # def add_service(self, service):
    #     """Add a service to the Connection.

    #     Attaches an instance of the :class:`~openstack.proxy.Proxy`
    #     class contained in
    #     :class:`~openstack.service_description.ServiceDescription`.
    #     The :class:`~openstack.proxy.Proxy` will be attached to the
    #     `Connection` by its ``service_type`` and by any ``aliases`` that
    #     may be specified.

    #     :param openstack.service_description.ServiceDescription service:
    #         Object describing the service to be attached. As a convenience,
    #         if ``service`` is a string it will be treated as a ``service_type``
    #         and a basic
    #         :class:`~openstack.service_description.ServiceDescription`
    #         will be created.
    #     """
    #     # If we don't have a proxy, just instantiate Proxy so that
    #     # we get an adapter.
    #     if isinstance(service, six.string_types):
    #         service = service_description.ServiceDescription(service)

    #     # Directly invoke descriptor of the ServiceDescription
    #     def getter(self):
    #         return service.__get__(self, owner=None)

    #     # Register the ServiceDescription class (as property)
    #     # with every known alias for a "runtime descriptor"
    #     all_types = [service.service_type] + service.aliases
    #     for attr_name in all_types:
    #         setattr(
    #             self.__class__,
    #             attr_name.replace('-', '_'),
    #             property(fget=getter)
    #         )
