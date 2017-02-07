#!/usr/bin/python

import sys
import os
import codecs
import xml.dom.minidom as mdom

def find_pspecs(folder):
    paks = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            paks.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return paks

def addText(doc, parent, text):
    cdata =doc.createTextNode(text)
    parent.appendChild(cdata)

def getTags(parent, childName):
    return [x for x in parent.childNodes if x.nodeType == x.ELEMENT_NODE if x.tagName == childName]

def getNodeText(node, tag, default=None):
    try:
        c = getTags(node, tag)[0].firstChild.data
    except:
        c = default
    return c

def newNode(doc, tag, text):
    node = doc.createElement(tag)
    cdata = doc.createTextNode(text)
    node.appendChild(cdata)
    return node

def fixIndent(doc, node):
    for x in node.childNodes:
        if x.nodeType == x.ELEMENT_NODE:
            if x.tagName == "Update":
                fixIndent(doc, x)
        else:
            x.data = "\n" + x.data[5:]

def fixTags(doc, hist):
    for update in hist.childNodes:
        if update.nodeType == update.ELEMENT_NODE:
            rno =  getNodeText(update, "Release")
            update.setAttribute("release", rno)
            if rno == "1":
                comment = newNode(doc, "Comment", "First release.")
                paker = getTags(getTags(doc.documentElement, "Source")[0], "Packager")[0]
                name = newNode(doc, "Name", getNodeText(paker, "Name"))
                email = newNode(doc, "Email", getNodeText(paker, "Email"))
            else:
                comment = newNode(doc, "Comment", "FIXHISTORY")
                name = newNode(doc, "Name", "FIXHISTORY")
                email = newNode(doc, "Email", "FIXHISTORY")
            update.replaceChild(comment, getTags(update, "Release")[0])
            addText(doc, update, "    ")
            update.appendChild(name)
            addText(doc, update, "\n            ")
            update.appendChild(email)
            addText(doc, update, "\n        ")

def fixPspec(path):
    doc = mdom.parse(path)
    pisi = doc.documentElement
    source = getTags(pisi, "Source")[0]
    history = getTags(source, "History")[0]
    item = source.removeChild(history)
    addText(doc, pisi, "\n    ")
    fixIndent(doc, item)
    fixTags(doc, item)
    pisi.appendChild(item)
    addText(doc, pisi, "\n")
    f = codecs.open(path,'w', "utf-8")
    f.write(doc.toxml())
    f.close()

pakages = find_pspecs(sys.argv[1])
for pak in pakages:
    fixPspec(os.path.join(pak, "pspec.xml"))
