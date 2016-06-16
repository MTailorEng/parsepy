#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


from parse_rest.core import ResourceRequestLoginRequired, ParseError
from parse_rest.connection import api_root, access_keys
from parse_rest.datatypes import ParseResource, ParseType
from parse_rest.query import QueryManager


class User(ParseResource):
    '''
    A User is like a regular Parse object (can be modified and saved) but
    it requires additional methods and functionality
    '''
    @classmethod
    def endpoint_root(cls):
        return '/'.join([api_root(), 'users'])

    PROTECTED_ATTRIBUTES = ParseResource.PROTECTED_ATTRIBUTES + [
        'username', 'sessionToken', 'emailVerified']

    def is_authenticated(self):
        return self.sessionToken is not None

    def authenticate(self, password=None, session_token=None):
        if self.is_authenticated(): return

        if password is not None:
            self = User.login(self.username, password)

        user = User.Query.get(objectId=self.objectId)
        if user.objectId == self.objectId and user.sessionToken == session_token:
            self.sessionToken = session_token

    def _assert_logged_in_or_master_key(self):
        '''Checks that master key is set or user is logged in.
        If user is logged in and master key is not set, returns extra headers
        that contain the session token.

        Otherwise returns an empty extra headers object.'''
        if 'master_key' in access_keys():
            return {}
        if hasattr(self, 'sessionToken'):
            return {'X-Parse-Session-Token': self.sessionToken}
        raise ResourceRequestLoginRequired('Master key or logged-in session required')

    def session_header(self):
        if not hasattr(self, 'sessionToken'):
            raise ResourceRequestLoginRequired('Logged-in session required')
        return {'X-Parse-Session-Token': self.sessionToken}

    def save(self, batch=False):
        session_header = self._assert_logged_in_or_master_key()
        url = self._absolute_url
        data = self._to_native()

        response = User.PUT(url, extra_headers=session_header, batch=batch, **data)

        def call_back(response_dict):
            self.updatedAt = response_dict['updatedAt']

        if batch:
            return response, call_back
        else:
            call_back(response)

    def delete(self):
        session_header = self._assert_logged_in_or_master_key()
        return User.DELETE(self._absolute_url, extra_headers=session_header)

    @staticmethod
    def signup(username, password, **kw):
        response_data = User.POST('', username=username, password=password, **kw)
        response_data.update({'username': username})
        return User(**response_data)

    @staticmethod
    def login(username, passwd):
        login_url = '/'.join([api_root(), 'login'])
        return User(**User.GET(login_url, username=username, password=passwd))

    @staticmethod
    def login_auth(auth):
        login_url = User.endpoint_root()
        return User(**User.POST(login_url, authData=auth))

    @staticmethod
    def request_password_reset(email):
        '''Trigger Parse\'s Password Process. Return True/False
        indicate success/failure on the request'''

        url = '/'.join([api_root(), 'requestPasswordReset'])
        try:
            User.POST(url, email=email)
            return True
        except ParseError:
            return False

    def _to_native(self):
        return dict([(k, ParseType.convert_to_parse(v, as_pointer=True))
                     for k, v in self._editable_attrs.items()])

    @property
    def className(self):
        return '_User'

    def __repr__(self):
        return '<User:%s (Id %s)>' % (getattr(self, 'username', None), self.objectId)


User.Query = QueryManager(User)
