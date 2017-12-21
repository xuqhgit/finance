# -*- coding: utf-8 -*-

import functools
from flask import render_template, request, make_response
import datetime
import json


def _json_serialize(v):
    if isinstance(v, datetime.datetime):
        return v.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return json.JSONEncoder.default(v)


def json_dumps(obj):
    return json.dumps(obj, default=_json_serialize, ensure_ascii=False)


def jview(arg):
    if isinstance(arg, str) or isinstance(arg, unicode):
        tpl_path = arg

        def wrapper_maker(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kargs):
                result = view_func(*args, **kargs)
                if isinstance(result, dict):
                    #
                    return render_template(tpl_path, **result)
                return result

            return wrapper

        return wrapper_maker
    else:
        view_func = arg

        @functools.wraps(view_func)
        def wrapper(*args, **kargs):
            result = view_func(*args, **kargs)
            if isinstance(result, str) or isinstance(result, unicode):
                return result
            if isinstance(result, dict) or isinstance(result, list) \
                    or isinstance(result, tuple):
                return json_dumps(result)
            return result

        return wrapper


def json_view(arg):
    if isinstance(arg, dict):
        headers = arg

        def wrapper_maker(view_func):
            @functools.wraps(view_func)
            def wrapper(*args, **kargs):
                _args = request.args
                callback = _args['callback'] if 'callback' in _args else None
                if request.method == 'POST':
                    _args = request.form
                    if 'callback' in _args:
                        callback = _args['callback']
                if callback:
                    resp_text = json_dumps(view_func(*args, **kargs))
                    resp_text = callback + '(' + resp_text + ')'
                else:
                    resp_text = json_dumps(view_func(*args, **kargs))
                resp = make_response(resp_text)
                resp.content_type = 'text/javascript; charset=utf-8'

                for h in headers:
                    resp.headers[h] = headers[h]
                resp.headers['Access-Control-Allow-Origin'] = '*'
                resp.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
                resp.headers['Access-Control-Allow-Headers'] = "Referer,Accept,Origin,User-Agent"
                return resp

            return wrapper

        return wrapper_maker
    else:
        view_func = arg
        @functools.wraps(view_func)
        def wrapper(*args, **kargs):
            resp = make_response(json_dumps(view_func(*args, **kargs)))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

        return wrapper
