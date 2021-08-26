# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import unittest

import pisi.context as ctx

class ContextTestCase(unittest.TestCase):
    
    def testConstness(self):
        const = ctx.const

        # test if we can get a const attribute?
        try:
            test = const.package_suffix
            self.assertNotEqual(test, "")
        except AttributeError:
            self.fail("Couldn't get const attribute")

        # test binding a new constant
        const.test = "test binding"
    
        # test re-binding (which is illegal)
        try:
            const.test = "test rebinding"
            # we shouldn't reach here
            self.fail("Rebinding a constant works. Something is wrong!")
        except:
            # we achived our goal with this error. infact, this is a
            # ConstError but we can't catch it directly here
            pass

        # test unbinding (which is also illegal)
        try:
            del const.test
            # we shouldn't reach here
            self.fail("Unbinding a constant works. Something is wrong!")
        except:
            # we achived our goal with this error. infact, this is a
            # ConstError but we can't catch it directly here
            pass

    def testConstValues(self):
        const = ctx.const

        constDict = {
            "actions_file": "actions.py",
            "setup_func": "setup",
            "metadata_xml": "metadata.xml"
            }
            
        for k in list(constDict.keys()):
            if hasattr(const, k):
                value = getattr(const, k)
                self.assertEqual(value, constDict[k])
            else:
                self.fail("Constants does not have an attribute named %s" % k)


suite = unittest.makeSuite(ContextTestCase)
