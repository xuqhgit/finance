#-*- coding: utf-8 -*-

import os
import sys
import base64

app_startup_dir = os.path.dirname(os.path.abspath(__file__))
if app_startup_dir not in sys.path:
    sys.path.insert(0, app_startup_dir)


from web import app

#app.debug = True

application = app