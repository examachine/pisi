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
 xmlext is a helper module for accessing XML files using
 xml.dom.minidom . It is a convenient wrapper for some
 DOM functions, and provides path based get/add functions
 as in KDE API.

 function names are mixedCase for compatibility with minidom,
 an 'old library'

 note: this is a particularly inefficient implementation of xmlext.
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import xml.dom.minidom as mdom
from xml.parsers.expat import ExpatError

import pisi

class XmlError(pisi.Error):
    "named this way because the class if mostly used with an import *"
    pass

# Document wrappers

def newDocument(tag):
    impl = mdom.getDOMImplementation()
    dom = impl.createDocument(None, tag, None)
    return dom.documentElement

def parse(filename):
    try:
        dom = mdom.parse(filename)
        return dom.documentElement
    except ExpatError, inst:
        raise Error(_("File '%s' has invalid XML: %s\n") % (fileName,
                                                            str(inst)))

def newNode(node, tag):
    return node.ownerDocument.createElement(tag)

def newTextNode(node, text):
    return node.ownerDocument.createTextNode(text)

# Node related wrappers

def getNodeAttribute(node, attrname):
    """get named attribute from DOM node"""
    if not node.hasAttribute(attrname):
        return None
    return node.getAttribute(attrname)

def getChildElts(node):
    """get only child elements"""
    return filter(lambda x:x.nodeType == x.ELEMENT_NODE, node.childNodes)

def getTagByName(parent, childName):
    return [x for x in parent.childNodes
            if x.nodeType == x.ELEMENT_NODE and x.tagName == childName]

def getNodeText(node, tagpath = ""):
    """get the first child and expect it to be text!"""
    if tagpath!="":
        node = getNode(node, tagpath)
    try:
        child = node.childNodes[0]
    except IndexError:
        return None
    except AttributeError: # no node by that name
        return None
    if child.nodeType == child.TEXT_NODE:
        # in any case, strip whitespaces...
        return child.data.strip()
    else:
        raise XmlError(_("getNodeText: Expected text node, got something else!"))

def getChildText(node_s, tagpath):
    """get the text of a child at the end of a tag path"""
    node = getNode(node_s, tagpath)
    if not node:
        return None
    return getNodeText(node)

def getNode(node, tagpath):
    """returns the *first* matching node for given tag path."""

    assert type(tagpath)==str
    tags = tagpath.split('/')
    assert len(tags)>0

    # iterative code to search for the path
    for tag in tags:
        currentNode = None
        for child in node.childNodes:
            if child.nodeType == node.ELEMENT_NODE and child.tagName == tag:
                currentNode = child
                break
        if not currentNode:
            return None
        else:
            node = currentNode
    return currentNode

def getAllNodes(node, tagPath):
    """retrieve all nodes that match a given tag path."""

    tags = tagPath.split('/')

    if len(tags) == 0:
        return []

    nodeList = [node] # basis case

    for tag in tags:
        results = map(lambda x: getTagByName(x, tag), nodeList)
        nodeList = []
        for x in results:
            nodeList.extend(x)
            pass # emacs indentation error, keep it here

        if len(nodeList) == 0:
            return []

    return nodeList

def createTagPath(node, tags):
    """create new child at the end of a tag chain starting from node
    no matter what"""
    if len(tags)==0:
        return node
    dom = node.ownerDocument
    for tag in tags:
        node = node.appendChild(dom.createElement(tag))
    return node

def addTagPath(node, tags, newnode=None):
    """add newnode at the end of a tag chain, smart one"""
    node = createTagPath(node, tags)
    if newnode:                     # node to add specified
        node.appendChild(newnode)
    return node    

def addNode(node, tagpath, newnode = None, branch=True):
    """add a new node at the end of the tree and returns it
    if newnode is given adds that node, too."""

    assert type(tagpath)==str
    tags = []
    if tagpath != "":
        tags = tagpath.split('/')           # tag chain
    else:
        addTagPath(node, [], newnode)
        return node #FIXME: is this correct!?!?
        
    assert len(tags)>0                  # we want a chain

    # iterative code to search for the path

    if branch:
        rem = 1
    else:
        rem = 0

    while len(tags) > rem:
        tag = tags.pop(0)
        nodeList = getTagByName(node, tag)
        if len(nodeList) == 0:          # couldn't find
            tags.insert(0, tag)         # put it back in
            return addTagPath(node, tags, newnode)
        else:
            node = nodeList[len(nodeList)-1]           # discard other matches
    else:
        # had only one tag..
        return addTagPath(node, tags, newnode)

    return node

def addText(node, tagPath, text, branch = True):
    newnode = newTextNode(node, text)
    return addNode(node, tagPath, newnode, branch = branch)
