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
from openstack import proxy
from openstack import resource
from openstack import exceptions

from opentelekom import otc_proxy

from opentelekom.cce.v3 import cluster as _cluster
from opentelekom.cce.v3 import cluster_node as _cluster_node
from opentelekom.cce.v3 import cluster_cert as _cluster_cert


class Proxy(otc_proxy.OtcProxy):

    # usually used only if endpoint is not registered yet officially
    # FIXME version discovery for CCE is inconsistent ti the handling elsewhere
    skip_discovery = True

    # ======== Cluster ========
    def clusters(self):
        """List all Clusters.

        :returns: a generator of
            (:class:`~otcextensions.sdk.cce.v3.cluster.Cluster`) instances
        """
        return self._list(_cluster.Cluster, paginated=False)

    def get_cluster(self, cluster):
        """Get the cluster by UUID.

        :param cluster: key id or an instance of
            :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`

        :returns: instance of
            :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`
        """
        return self._get(
            _cluster.Cluster, cluster,
        )

    def create_cluster(self, **attrs):
        """Create a cluster from attributes.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`,
            comprised of the properties on the Cluster class.

        :returns: The results of cluster creation
        :rtype: :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`
        """
        return self._create(
            _cluster.Cluster, prepend_key=False, **attrs
        )

    def find_cluster(self, name_or_id, ignore_missing=True):
        """Find a single cluster.

        :param name_or_id: The name or ID of a cluster
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the group does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent group.

        :returns: ``None``
        """
        return self._find(
            _cluster.Cluster, name_or_id,
            ignore_missing=ignore_missing,
        )

    def delete_cluster(self, cluster, ignore_missing=True):
        """Delete a cluster.

        :param cluster: The value can be the ID of a cluster
             or a :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`
             instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the group does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent cluster.
        """
        return self._delete(
            _cluster.Cluster, cluster, ignore_missing=ignore_missing,
        )

    def get_cluster_certificates(self, cluster):
        """Get the certificates of a cluster.

        :param cluster: key id or an instance of
            :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`

        :returns: instance of
            :class:`~otcextensions.sdk.cce.v3.cluster_cert.ClusterCertificates`
        """
        cluster = self._get_resource(_cluster.Cluster, cluster)
        return self._get(
            _cluster_cert.ClusterCertificate, cluster_id=cluster.id,
            requires_id=False
        )

    def wait_for_status(self, cluster, status='Available', failures=None,
                        interval=15, wait=1500):
        """Wait for a cluster to be in a particular status.

        :param res: The resource to wait on to reach the specified status.
                    The resource must have a ``status`` attribute.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
                 has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
                ``status`` attribute.
        """
        failures = ['Error'] if failures is None else failures
        return resource.wait_for_status(
            self, cluster, status, failures, interval, wait, attribute="status")

    def wait_for_delete(self, res, interval=15, wait=1200):
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait)

    def get_cluster_certs(self, cluster):
        """Get user certificates for the kubectl access to the 
        cluster node given by it's UUID.

        :param cluster: key id or an instance of
            :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`

        :returns: instance of
            :class:`~otcextensions.sdk.cce.v3.cluster_cert.ClusterCert`
        """
        cluster = self._get_resource(_cluster.Cluster, cluster)
        return self._get(
            _cluster_cert.ClusterCertificate,
            requires_id=False,
            cluster_id=cluster.id,
        )


    # ======== Cluster Nodes ========
    def cluster_nodes(self, cluster):
        """List all Cluster nodes.

        :param cluster: The value can be the ID of a cluster
             or a :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`
             instance.

        :returns: a generator of
            (:class:`~otcextensions.sdk.cce.v3.cluster_node.ClusterNode`)
            instances
        """
        cluster = self._get_resource(_cluster.Cluster, cluster)
        return self._list(
            _cluster_node.ClusterNode, cluster_id=cluster.id,
            paginated=False
        )

    def get_cluster_node(self, cluster, node_id):
        """Get the cluster node by it's UUID.

        :param cluster: key id or an instance of
            :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`
        :param node_id: Cluster node id to be fetched

        :returns: instance of
            :class:`~otcextensions.sdk.cce.v3.cluster_node.ClusterNode`
        """
        cluster = self._get_resource(_cluster.Cluster, cluster)
        return self._get(
            _cluster_node.ClusterNode,
            node_id,
            cluster_id=cluster.id,
        )

    def find_cluster_node(self, cluster, node):
        """Find the cluster node by it's UUID or name.

        :param cluster: key id or an instance of
            :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`
        :param node: Cluster node id or name to be fetched

        :returns: instance of
            :class:`~otcextensions.sdk.cce.v3.cluster_node.ClusterNode`
        """
        cluster = self._get_resource(_cluster.Cluster, cluster)
        return self._find(
            _cluster_node.ClusterNode,
            node,
            cluster_id=cluster.id,
        )

    def delete_cluster_node(self, cluster, node, ignore_missing=True):
        """Delete nodes from the cluster.

        :param cluster: The value can be the ID of a cluster
             or a :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`
             instance.
        :param node: The value can be the ID of a cluster node
             or a :class:`~otcextensions.sdk.cce.v3.cluster_node.ClusterNode`
             instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the node does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent cluster node.
        """
        cluster = self._get_resource(_cluster.Cluster, cluster)
        return self._delete(
            _cluster_node.ClusterNode,
            node,
            ignore_missing=ignore_missing,
            cluster_id=cluster.id,
        )

    def create_cluster_node(self, cluster, **attrs):
        """Add a new node to the cluster.

        :param cluster: The value can be the ID of a cluster
             or a :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`
             instance.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~otcextensions.sdk.cce.v3.cluster_node.ClusterNode`,
            comprised of the properties on the ClusterNode class.
        :returns: The results of config creation
        :rtype: :class:`~otcextensions.sdk.cce.v3.cluster_node.ClusterNode`
        """
        cluster = self._get_resource(_cluster.Cluster, cluster)
        return self._create(
            _cluster_node.ClusterNode,
            cluster_id=cluster.id,
            **attrs
        )

    def wait_for_status_cluster_nodes(self, cluster, status="Active", failures=None, interval=15, wait=1200, attribute='status'):
        def _all_nodes_selector():
            return self.cluster_nodes(cluster)

        return super().wait_for_status_all(_all_nodes_selector, status, 
            failures, interval, wait, attribute)

    def wait_for_status_nodes(self, cluster, nodes, status="Active", failures=None, interval=15, wait=1200, attribute='status'):
        node_ids = set(map( lambda node: node.id if isinstance(node, _cluster_node.ClusterNode) else node,
            nodes ))
        
        def _nodes_by_id_selector():
            return filter( lambda node: node.id in node_ids, 
                self.cluster_nodes(cluster))

        return super().wait_for_status_all(_nodes_by_id_selector, status, 
            failures, interval, wait, attribute)



    def delete_cluster_nodes(self, cluster, ignore_missing=True):
        """Delete nodes selected by list_func from the cluster.

        :param cluster: The value can be the ID of a cluster
             or a :class:`~otcextensions.sdk.cce.v3.cluster.Cluster`
             instance.
        :param node: The value can be the ID of a cluster node
             or a :class:`~otcextensions.sdk.cce.v3.cluster_node.ClusterNode`
             instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the node does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent cluster node.
        """
        cluster = self._get_resource(_cluster.Cluster, cluster)
        for node in self.cluster_nodes(cluster):
            self.delete_cluster_node(cluster.id, node)

    def wait_for_delete_cluster_nodes(self, cluster, interval=15, wait=1200, attribute='status'):
        def _all_nodes_selector():
            return self.cluster_nodes(cluster)

        return super().wait_for_delete_all(_all_nodes_selector, interval, wait, attribute)

    def wait_for_delete_nodes(self, cluster, nodes, interval=15, wait=1200, attribute='status'):
        node_ids = set(map(
            lambda node: node.id if isinstance(node, _cluster_node.ClusterNode) else node,
            nodes ))            
        def _nodes_by_id_selector():
            return filter( lambda node: node.id in node_ids, 
                self.cluster_nodes(cluster))

        return super().wait_for_delete_all(_nodes_by_id_selector, interval, wait, attribute)
