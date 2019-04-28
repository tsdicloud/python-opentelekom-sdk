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

from opentelekom.kms.v1 import cmk as _cmk
#from opentelekom.dms.v1.0 import subscription as _subscription
from opentelekom import otc_proxy
from openstack import resource


class Proxy(otc_proxy.OtcProxy):

    def create_key(self, **kwargs):
        """Create a encrypt key for encrypt a data key

        :param dict kwargs: Keyword arguments which will be used to overwrite a
                            :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        :rtype: :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        """
        return self._create(_cmk.CustomerMasterKey, prepend_key=False, **kwargs)

    def _get_key_obj(self, key, **kwargs):
        if isinstance(key, str):
            kwargs.update({"key_id": key})
            return _cmk.CustomerMasterKey.new(**kwargs)
        else:
            return key

    def get_key(self, key, **kwargs):
        """Describe a encrypt key by given key id or key object

        :param key: key id or an instance of :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        :param dict kwargs: Keyword arguments which will be used to describe
                            the key. e.g. sequence
        :rtype: :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        """
        key_obj = self._get_key_obj(key, **kwargs)
        return key_obj.describe(self, key_id=key_obj.key_id, sequence=key_obj.sequence)

    def keys(self, **query):
        """List all keys.

        :param dict kwargs: Keyword arguments which will be used to list keys.
                            limit, marker, sequence are allowed.

        """
        return self._list(_cmk.CustomerMasterKey, base_path="/kms/list-keys", **query)

    def enable_key(self, key, **params):
        """Enable a key

        :param key: key id or an instance of :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        :param dict kwargs: Keyword arguments which will be used to enable key.
                            sequence is allowed.
        :rtype: :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        """

        key_obj = self._get_key_obj(key, **params)
        return key_obj.enable(self, key_id=key_obj.key_id, sequence=key_obj.sequence)

    def disable_key(self, key, **params):
        """Disable a key

        :param key: key id or an instance of :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        :param dict kwargs: Keyword arguments which will be used to disable
                            key. sequence is allowed.
        :rtype: :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        """
        key_obj = self._get_key_obj(key, **params)
        return key_obj.disable(self, key_id=key_obj.key_id, sequence=key_obj.sequence)

    def schedule_delete_key(self, key, pending_days=7, **params):
        """Schedule a key deletion

        :param key: key id or an instance of :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        :param pending_days: Pending days before deletion, allow 7 to 1096
        :param dict kwargs: Keyword arguments which will be used to schedule a
                            key deletion. sequence is allowed.
        :rtype: :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        """
        key_obj = self._get_key_obj(key, **params)
        return key_obj.schedule_delete(self, key_id=key_obj.key_id, sequence=key_obj.sequence,
            pending_days=pending_days)

    def cancel_delete_key(self, key, **params):
        """Cancel a key deletion

        :param key: key id or an instance of :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        :param dict kwargs: Keyword arguments which will be used to schedule a
                            key deletion. sequence is allowed.
        :rtype: :class:`~openstack.kms.v1.cmk.CustomrMasterKey`
        """
        key_obj = self._get_key_obj(key, **params)
        return key_obj.cancel_delete(self, key_id=key_obj.key_id, sequence=key_obj.sequence)
