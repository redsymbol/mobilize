import unittest
from mobilize import common

class TestCommon(unittest.TestCase):
    def test_classvalue(self):
        self.assertSequenceEqual('mwu-elem', common.classvalue())
        self.assertSequenceEqual('mwu-elem mwu-elem-alpha mwu-elem-beta', common.classvalue('alpha', 'beta'))

    def test_classname(self):
        self.assertSequenceEqual('mwu-elem', common.classname())
        self.assertSequenceEqual('mwu-elem-alpha', common.classname('alpha'))

    def test_idname(self):
        self.assertSequenceEqual('mwu-elem-42', common.idname(42))
        self.assertSequenceEqual('mwu-elem-0', common.idname(0))
        self.assertSequenceEqual('mwu-elem-blah', common.idname('blah'))
