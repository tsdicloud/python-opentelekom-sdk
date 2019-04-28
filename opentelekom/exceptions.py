#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Extended exception format for Open Telekom Cloud
"""

from openstack import HttpException
import six

class OtcHttpException(HttpException):
    def __init__(self, message=None, details=None, response=None,
                 request_id=None, url=None, method=None,
                 http_status=None, cause=None, code=None):
        super(OtcHttpException, self).__init__(message=message, cause=cause)
        self.details = details
        self.response = response
        self.request_id = request_id
        self.url = url
        self.method = method
        self.http_status = http_status
        self.code = code

    def __unicode__(self):
        msg = self.__class__.__name__ + ": " + self.message
        if self.details:
            msg += ", " + six.text_type(self.details)
        return msg

    def __str__(self):
        return self.__unicode__()


class BadRequestException(OtcHttpException):
    """HTTP 400 Bad Request."""
    pass

class NotFoundException(OtcHttpException):
    """HTTP 404 Not Found."""
    pass

class ConflictException(OtcHttpException):
    """HTTP 409 Conflict."""
    pass

class ResourceNotFound(OtcHttpException):
    """No resource exists with that name or id."""
    pass

