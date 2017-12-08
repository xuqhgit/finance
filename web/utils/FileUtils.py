# coding:utf-8

# @author:apple
# @date:16/4/29

import os

file_path = 'static/file/'

_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

_static_path = '%s/static' % _dir
_static_file_path = '%s/static/file/' % _dir
_static_components_path = '%s/static/components/' % _dir
_template_path = '%s/template/' % _dir


def get_file(path):
    if not os.path.exists(file_path + path):
        return None
    file_object = open(path)
    try:
        content = file_object.read()
        return content
    finally:
        file_object.close()
    return None


def write_data(path, data):
    file_object = open(file_path + path, 'w')
    file_object.write(data)
    file_object.close()
