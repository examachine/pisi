# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Authors:  Eray Ozkural <eray@pardus.org.tr>
#           Baris Metin <baris@pardus.org.tr
#           Gurer Ozen <gurer@pardus.org.tr>

"""
 XmlFile class further abstracts a dom object using the
 high-level dom functions provided in xmlext module (and sorely lacking
 in xml.dom :( )

 function names are mixedCase for compatibility with minidom,
 an 'old library'

 note: this is a particularly inefficient implementation of xmlfile
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import xml.dom.minidom as mdom
from xml.parsers.expat import ExpatError
import codecs

import pisi
from pisi.file import File

class Error(pisi.Error):
    "named this way because the class if mostly used with an import *"
    pass

class XmlFile(object):
    """A class to help reading and writing an XML file"""

    def __init__(self, tag):
        self.rootTag = tag

    def newDocument(self):
        """clear DOM"""
        impl = mdom.getDOMImplementation()
        self.doc = impl.createDocument(None, self.rootTag, None)

    def unlink(self):
        """deallocate DOM structure"""
        self.doc.unlink()
        del self.doc

    def rootNode(self):
        """returns root document element"""
        return self.doc.documentElement

    def readxml(self, uri, tmpDir = '/tmp'):
        uri = File.make_uri(uri)
        localpath = File.download(uri, tmpDir)

        try:
            self.doc = mdom.parse(localpath)
        except ExpatError, inst:
            raise Error(_("File '%s' has invalid XML: %s\n") % (fileName,
                                                                str(inst)))

    def writexml(self, fileName):
        f = codecs.open(fileName,'w', "utf-8")
        f.write(self.doc.toprettyxml())
        f.close()

    def verifyRootTag(self):
        actual_roottag = self.rootNode().tagName
        if actual_roottag != self.rootTag:
            raise Error(_("Root tagname %s not identical to %s as expected") %
                        (actual_roottag, self.rootTag) )

    # construction helpers

    def newNode(self, tag):
        return self.doc.createElement(tag)

    def newTextNode(self, text):
        return self.doc.createTextNode(text)

    def newAttribute(self, attr):
        return self.doc.createAttribute(attr)

    # read helpers

    def getNode(self, tagPath = ""):
        """returns the *first* matching node for given tag path."""
        self.verifyRootTag()
        return getNode(self.doc.documentElement, tagPath)

    def getNodeText(self, tagPath):
        """returns the text of *first* matching node for given tag path."""
        node = self.getNode(tagPath)
        if not node:
            return None
        return getNodeText(node)

    def getAllNodes(self, tagPath):
        """returns all nodes matching a given tag path."""
        self.verifyRootTag()
        return getAllNodes(self.doc.documentElement, tagPath)

    def getChildren(self, tagpath):
        """ returns the children of the given path"""
        node = self.getNode(tagpath)
        return node.childNodes

    # get only elements of a given type
    #FIXME:  this doesn't work
    def getChildrenWithType(self, tagpath, type):
        """ returns the children of the given path, only with given type """
        node = self.getNode(tagpath)
        return filter(lambda x:x.nodeType == type, node.childNodes)

    # get only child elements
    def getChildElts(self, tagpath):
        """ returns the children of the given path, only with given type """
        node = self.getNode(tagpath)
        try:
            return filter(lambda x:x.nodeType == x.ELEMENT_NODE,
                          node.childNodes)
        except AttributeError:
            return None

    # write helpers

    def addNode(self, tagPath, newnode = None):
        "this adds the newnode under given tag path"
        self.verifyRootTag()
        return addNode(self.doc.documentElement, tagPath, newnode)

    def addNodeUnder(self, node, tagPath, newnode = None):
        "this adds the new stuff under node and then following tag path"
        self.verifyRootTag()
        return addNode(node, tagPath, newnode)

    def addChild(self, newnode):
        "add a new child node right under root element document"
        self.doc.documentElement.appendChild(newnode)

    def addText(self, node, text):
        "add text to node"
        node.appendChild(self.newTextNode(text))

    def addTextNode(self, tagPath, text):
        "add a text node with given tag path"
        node = self.addNode(tagPath, self.newTextNode(text))
        return node

    def addTextNodeUnder(self, node, tagPath, text):
        "add a text node under given node with tag path (phew)"
        return self.addNodeUnder(node, tagPath, self.newTextNode(text))
