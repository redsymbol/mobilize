import unittest

class TestSecurity(unittest.TestCase):
    def test_phpnuke_sqlinjection_urlmatch(self):
        from mobilize.secure import _phpnuke_sqlinjection_urlmatch
        testurls = {
            "/modules.php?name=Downloads&d_op=modifydownloadrequest&lid=-1%20UNION%20SELECT%200,username,user_id,user_password,name,user_email,user_level,0,0%20FROM%20nuke_users",
            "/modules.php?name=Downloads&d_op=viewsdownload&sid=-1/**/UNION/**/SELECT/**/0,0,aid,pwd,0,0,0,0,0,0,0,0/**/FROM/**/nuke_authors/**/WHERE/**/radminsuper=1/**/LIMIT/**/1/*",
            "/modules.php?name=Journal&file=search&bywhat=aid&exact=1&forwhat=saint'+UNION+SELECT+0,0,pwd,0,0,0,0,0,0+FROM+nuke_authors+WHERE+radminsuper=1+LIMIT+1/*",
            "/modules.php?name=Search&type=comments&query=not123exists&instory=+UNION+SELECT+0,0,pwd,0,aid+FROM+nuke_authors",
            "/index.php?kala=p0hh+UNION+ALL+SELECT+1,2,3,pwd,5+FROM+nuke_authors/*",
            "/index.php?kala=p0hh+UNION+ALL+SELECT+1,2,3,pwd,5+FROM+nuke_authors/%2a",
            }
        for testurl in testurls:
            self.assertTrue(_phpnuke_sqlinjection_urlmatch(testurl), testurl)

    def test_vulntag(self):
        from mobilize.secure import (
            vulntag,
            get_vultags,
            )
        def dummy1():
            pass
        self.assertSetEqual(set(), get_vultags(dummy1))
                            
        @vulntag('mwu-foo', 'CVE-1234-567')
        def dummy2():
            pass
        self.assertSetEqual({'mwu-foo', 'cve-1234-567'},
                            get_vultags(dummy2))
