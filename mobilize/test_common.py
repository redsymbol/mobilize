import unittest
from mobilize import common

class TestCommon(unittest.TestCase):
    def test_classvalue(self):
        self.assertSequenceEqual('mwu-melem', common.classvalue())
        self.assertSequenceEqual('mwu-melem mwu-melem-alpha mwu-melem-beta', common.classvalue('alpha', 'beta'))

    def test_classname(self):
        self.assertSequenceEqual('mwu-melem', common.classname())
        self.assertSequenceEqual('mwu-melem-alpha', common.classname('alpha'))

    def test_idname(self):
        self.assertSequenceEqual('mwu-melem-42', common.idname(42))
        self.assertSequenceEqual('mwu-melem-0', common.idname(0))
        self.assertSequenceEqual('mwu-melem-blah', common.idname('blah'))
