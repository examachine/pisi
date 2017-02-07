#!/usr/bin/python

import os

def postInstall():
    os.system("ls -al > /tmp/SIK")
