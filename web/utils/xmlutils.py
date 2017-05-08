# coding:utf-8

# @author:apple
# @date:16/1/18
import xml.dom.minidom

import xml.etree.ElementTree as ET

class XmlUtils(object):
    """
        xml文件工具类
    """

    def __init__(self, path):
        #d = xml.dom.minidom.parseString(xmlString)
        d = xml.dom.minidom.parse(path)
        self.dom = d
        self.root = d.documentElement


    def getElementById(self, id, tagName):
        root = self.root
        elements = root.getElementsByTagName(tagName)
        for element in elements:
            if element.hasAttribute('id') and element.getAttribute('id') == id:
                return element
        return None

