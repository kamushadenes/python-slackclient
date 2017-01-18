import json

import requests
import six

import sys
import platform
from .version import __version__

class SlackRequest(object):
    def __init__(self):
        client_name = __name__.split('.')[0]  # __name__ returns 'slackclient._slackrequest', we only want 'slackclient'
        client_version = __version__  # Version is returned from version.py

        # Construct the user-agent header with the package info, Python version and OS version.
        self.default_user_agent = {"client": "{0}/{1}".format(client_name, client_version),
                      "python": "Python/{0}.{1}.{2}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]),
                      "system": "{0}/{1}".format(platform.system(), platform.release())}

        self.custom_user_agent = None

    def get_user_agent(self):
        # Check for custom user-agent and append if found
        if self.custom_user_agent:
            custom_ua_string = " ".join([ "/".join(client_info) for client_info in self.custom_user_agent])
            self.default_user_agent['custom'] = custom_ua_string

        # Concatenate and format the user-agent string to be passed into request headers
        ua_string = []
        for key, val in self.default_user_agent.items():
            ua_string.append(val)

        user_agent_string = " ".join(ua_string)
        return user_agent_string

    def append_user_agent(self, name, version):
        name = str.replace(name, "/", ":")
        version = str.replace(name, "/", ":")
        if self.custom_user_agent:
            self.custom_user_agent.append([name, version])
        else:
            self.custom_user_agent = [ [name, version] ]

    def do(self, token, request="?", post_data=None, domain="slack.com"):
        """
        Perform a POST request to the Slack Web API

        Args:
            token (str): your authentication token
            request (str): the method to call from the Slack API. For example: 'channels.list'
            post_data (dict): key/value arguments to pass for the request. For example:
                {'channel': 'CABC12345'}
            domain (str): if for some reason you want to send your request to something other
                than slack.com
        """

        # Pull file out so it isn't JSON encoded like normal fields.
        # Only do this for requests that are UPLOADING files; downloading files
        # use the 'file' argument to point to a File ID.
        post_data = post_data or {}
        upload_requests = ['files.upload']
        files = None
        if request in upload_requests:
            files = {'file': post_data.pop('file')} if 'file' in post_data else None

        for k, v in six.iteritems(post_data):
            if not isinstance(v, six.string_types):
                post_data[k] = json.dumps(v)

        url = 'https://{0}/api/{1}'.format(domain, request)
        post_data['token'] = token
        headers = {'user-agent': self.get_user_agent()}

        return requests.post(url, headers=headers, data=post_data, files=files)
