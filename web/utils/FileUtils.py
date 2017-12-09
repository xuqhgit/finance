# coding:utf-8

# @author:apple
# @date:16/4/29

import os

file_path = 'static/file/'

_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
web_dir = _dir
_static_path = '%s/static' % _dir
_static_file_path = '%s/static/file/' % _dir
_static_components_path = '%s/static/components/' % _dir
_template_path = '%s/template/' % _dir


def get_static_file(path):
    file_dir = _dir + "/" + file_path + path
    if not os.path.exists(file_dir):
        return None
    file_object = open(file_dir)
    try:
        content = file_object.read()
        return content
    finally:
        file_object.close()
    return None


def write_static_data(path, data):
    file_dir = _dir+"/"+file_path + path
    _file_dir = os.path.split(file_dir)[0]
    if not os.path.isdir(_file_dir):
        os.makedirs(_file_dir)
    file_object = open(file_dir, 'w')
    file_object.write(data)
    file_object.close()
