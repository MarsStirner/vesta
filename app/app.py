# -*- coding: utf-8 -*-
from flask import Flask
import config

app = Flask(__name__)
app.config.from_object(config)

from blueprints.admin.app import module as admin
# from blueprints.api.app import module as api
# from blueprints.soap.app import module as soap

app.register_blueprint(admin, url_prefix='/{0}'.format(admin.name))
# app.register_blueprint(api, url_prefix='/{0}'.format(api.name))
# app.register_blueprint(soap, url_prefix='/{0}'.format(soap.name))

# Import all views
from views import *