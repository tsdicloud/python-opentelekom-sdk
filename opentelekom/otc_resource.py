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

from openstack import resource

class OtcResource(resource.Resource):

    def _translate_response(self, response, has_body=None, error_message=None):
        """ Open Telekom has non-uniform formats for error details,
            so we try to adapte the different formats to get uesful information out of exceptions """
        emsg = None 
        if has_body is None:
            has_body = self.has_body
        if has_body:
            oerror = response.json()
            if "code" in oerror:
                emsg = "[" + oerror['code']  + "] " + oerror['message'] +"\n"
            elif "error_code" in oerror:
                emsg = "[" + oerror['error_code']  + "] " + oerror['error_msg'] +"\n"
            else:
                emsg = None 
        super()._translate_response(response, has_body, error_message=emsg)
