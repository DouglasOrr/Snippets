from .. import server
from nose.tools import eq_


def test_hello():
    eq_('Welcome to MBTAI', server.hello())
