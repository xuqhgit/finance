# coding:utf-8

# @author:apple
# @date:16/4/29

import os
class FileUtils(object):
    """
        
    """

    def __init__(self):
        pass

    @staticmethod
    def get_file(path):
        if not os.path.exists(path):
            return None
        file_object = open(path)
        try:
            content = file_object.read()
            return content
        finally:
            file_object.close()
        return None
