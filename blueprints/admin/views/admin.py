# -*- encoding: utf-8 -*-
import re
import os
from datetime import datetime

from flask import render_template, abort, request, redirect, jsonify, send_from_directory, url_for, json, current_app
from flask import flash, session
from jinja2 import TemplateNotFound
from ..app import module
from app.lib.data import Collections, Dictionary, DictionaryNames


@module.route('/')
def index():
    obj = DictionaryNames()
    data = obj.get_list()
    try:
        return render_template('{0}/index.html'.format(module.name), data=data)
    except TemplateNotFound:
        abort(404)


@module.route('/dict_edit/<_id>/')
def dict_edit(_id):
    obj = DictionaryNames()
    info = obj.get_by_id(_id)
    collections = Collections()
    if not info or 'code' not in info or info['code'] not in collections.get_list():
        abort(404)
    try:
        return render_template('{0}/dict_edit.html'.format(module.name), info=info)
    except TemplateNotFound:
        abort(404)