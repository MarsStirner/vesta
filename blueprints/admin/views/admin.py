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
    data = obj.get_list({'code': {'$ne': 'dict_names'}}, sort=[('oid', 1), ('code', 1)])
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
    collection = Dictionary(info['code'])
    # TODO: get fields for linked choose with other collection
    data = obj.get_list({'version': {'$exists': True}})
    fields = _get_fields(info['code'])
    try:
        return render_template('{0}/dict_edit.html'.format(module.name), info=info, data=data, fields=fields)
    except TemplateNotFound:
        abort(404)


@module.route('/dict_view/<_id>/')
def dict_view(_id):
    obj = DictionaryNames()
    info = obj.get_by_id(_id)
    collections = Collections()
    if not info or 'code' not in info or info['code'] not in collections.get_list():
        abort(404)
    collection = Dictionary(info['code'])
    # TODO: get fields for linked choose with other collection
    data = obj.get_list({'version': {'$exists': True}})
    fields = _get_fields(info['code'])
    try:
        return render_template('{0}/dict_view.html'.format(module.name), info=info, data=data, fields=fields)
    except TemplateNotFound:
        abort(404)


@module.route('/ajax_fields/<_id>')
def get_fields(_id):
    pass


def _get_fields(code):
    obj = Dictionary(code)
    document = list(obj.get_list(limit=1))
    if document[0]:
        return document[0].keys()
    return []
