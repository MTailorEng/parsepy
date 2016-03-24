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

from parse_rest.connection import api_root
from parse_rest.datatypes import ParseResource
from parse_rest.query import QueryManager


class Installation(ParseResource):
    @classmethod
    def endpoint_root(cls):
        return '/'.join([api_root(), 'installations'])


class Push(ParseResource):
    @classmethod
    def endpoint_root(cls):
        return '/'.join([api_root(), 'push'])

    @classmethod
    def _send(cls, data, where=None, **kw):
        if where:
            kw['where'] = where

            # allow channels to be specified even if "where" is as well
            if "channels" in kw:
                kw['where']["channels"] = kw.pop("channels")

        return cls.POST('', data=data, **kw)

    @classmethod
    def alert(cls, data, where=None, **kw):
        cls._send(data, where=where, **kw)

    @classmethod
    def message(cls, message, where=None, **kw):
        cls._send({'alert': message}, where=where, **kw)

Installation.Query = QueryManager(Installation)
