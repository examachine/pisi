#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.dom.minidom as mdom
import codecs
import os

folder = "/var/lib/pisi"

def saveMetadata(data, file):
    if data:
        f = codecs.open(file, 'w', "utf-8")
        f.write(data)
        f.close()
        return True

def getNodeText(node, tag, default=None):
    try   : c = getTags(node, tag)[0].firstChild.data
    except: c = default
    return  c

def getTags(parent, childName):
    return [x for x in parent.childNodes if x.nodeType == x.ELEMENT_NODE if x.tagName == childName]

def addText(dom, parent, text):
    cdata = dom.createTextNode(text)
    parent.appendChild(cdata)

def fixMetadata(metadata):
    dom = mdom.parse(metadata)
    pisi = dom.documentElement
    
    package = getTags(pisi, "Package")[0]
    history = getTags(package, "History")[0]
    item = package.removeChild(history)
    
    for update in history.childNodes:
        if update.nodeType == update.ELEMENT_NODE:
            try:
                rno =  getNodeText(update, "Release")[6:-5]
            except TypeError:
                return None
            update.setAttribute("release", rno)
            release = getTags(update, "Release")[0]
            update.removeChild(release)
    
    addText(dom, package, "        ")
    package.appendChild(item)
    addText(dom, package, "\n    ")
    return dom.toxml()

def findMetadata():
    for root, dirs, files in os.walk(folder):
        if "metadata.xml" in files:
            yield (root + '/metadata.xml')

for file in findMetadata():
    if saveMetadata(fixMetadata(file), file):
        print "Güncellendi          : ", file
    else:
        print "Hiç bir şey yapılmadı: ", file
