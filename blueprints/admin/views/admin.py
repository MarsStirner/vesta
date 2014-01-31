# -*- encoding: utf-8 -*-
import re
import os
from datetime import datetime

from flask import render_template, abort, request, redirect, jsonify, send_from_directory, url_for, json, current_app
from flask import flash, session
from jinja2 import TemplateNotFound
from ..app import module
from app.lib.data import Collections, Dictionary, DictionaryNames
from app.lib.worker import Worker
from app.lib.utils.tools import jsonify as vesta_jsonify, json


@module.route('/')
def index():
    obj = DictionaryNames()
    data = obj.get_list({'code': {'$ne': 'dict_names'}}, sort=[('oid', 1), ('code', 1)])
    try:
        return render_template('{0}/index.html'.format(module.name), data=data)
    except TemplateNotFound:
        abort(404)


@module.route('/dict_edit/<_id>/', methods=['GET', 'POST'])
def dict_edit(_id):
    obj = DictionaryNames()
    info = obj.get_by_id(_id)
    collections = Collections()
    if not info or 'code' not in info:# or info['code'] not in collections.get_list():
        flash(u'Коллекция не существует или пуста')
        abort(404)

    if request.method == 'POST':
        worker = Worker(info['code'])
        try:
            worker.link_collection(request.form.get('linked_collection'),
                                   request.form.get('origin_field'),
                                   request.form.get('linked_field'))
            info = obj.get_by_id(_id)
        except Exception, e:
            flash(e, 'error')
        else:
            flash(u'Справочник успешно обновлён', 'info')
            return redirect(url_for('.dict_edit', _id=_id))
    data = dict()
    fields = dict()
    documents = list()
    collection = Dictionary(info['code'])
    linked_dict = obj.get_list({'version': {'$exists': True}})
    if info['code'] in collections.get_list():
        fields = _get_fields(info['code'])
        documents = collection.get_list(sort=[('id', 1)])
    try:
        return render_template('{0}/dict_edit.html'.format(module.name),
                               info=info,
                               data=linked_dict,
                               fields=fields,
                               documents=documents)
    except TemplateNotFound:
        abort(404)


@module.route('/dict_view/<_id>/')
def dict_view(_id):
    obj = DictionaryNames()
    info = obj.get_by_id(_id)
    collections = Collections()
    if not info or 'code' not in info or info['code'] not in collections.get_list():
        flash(u'Коллекция не существует или пуста')
        abort(404)
    collection = Dictionary(info['code'])
    data = obj.get_list({'version': {'$exists': True}})
    fields = _get_fields(info['code'])
    try:
        return render_template('{0}/dict_view.html'.format(module.name),
                               info=info,
                               data=data,
                               fields=fields,
                               documents=collection.get_list(sort='id', limit=300))
    except TemplateNotFound:
        abort(404)


def _get_linked_dict(document, collection):
    # Если в документе задана привязка к справочнику - используем её
    if 'linked_collection' in document:
        obj_names = DictionaryNames()
        linked_dict = obj_names.get_by_code(document['linked_collection'])
        return linked_dict

    # Иначе смотрим на привязку самого справочника
    try:
        linked_dict = collection['linked']['collection']
    except AttributeError:
        return None
    except KeyError:
        return None
    else:
        return linked_dict

@module.route('/doc/edit/<code>/<_id>/', methods=['GET', 'POST'])
def doc_edit(code, _id):
    dict_names = DictionaryNames()
    current = dict_names.get_by_code(code)
    linked = None
    linked_code = None
    linked_docs = []
    linked_dict = dict()
    linked_dicts = dict_names.get_list({'version': {'$exists': True}})
    obj = Dictionary(code)
    document = obj.get_document({'_id': _id})

    linked_dict = _get_linked_dict(document, current)
    if linked_dict:
        linked_code = linked_dict['code']
        linked = Dictionary(linked_code)
        linked_docs = linked.get_list()

    if request.method == 'POST':
        data = dict()
        if request.form:
            for key, value in request.form.items():
                data[key] = value
        linked_id = data.pop('linked')
        _post_linked_code = data.pop('linked_collection')
        data.update({'_id': _id})
        if _post_linked_code:
            if _post_linked_code != linked_code:
                linked_code = _post_linked_code
                data.update({'linked_collection': linked_code})
            else:
                obj.unset_attr(_id, 'linked_collection')

            if linked_id:
                linked = Dictionary(linked_code)
                linked_document = linked.get_document({'_id': linked_id})
                data.update({linked_code: linked_document})
            else:
                obj.unset_attr(_id, linked_code)
        try:
            obj.add_document(data)
        except Exception, e:
            flash(e, 'error')
        else:
            flash(u'Документ сохранён', 'info')
            return redirect(url_for('.doc_edit', code=code, _id=_id))

    if document:
        return render_template('{0}/doc_edit.html'.format(module.name),
                               current_dict=current,
                               document=document,
                               linked_docs=linked_docs,
                               linked_dicts=linked_dicts,
                               linked_dict=linked_dict)


@module.route('/ajax_fields/')
@module.route('/ajax_fields/<code>')
def get_fields(code=None):
    if code:
        return jsonify(result=_get_fields(code))


@module.route('/get_documents/')
@module.route('/get_documents/<code>')
def get_documents(code=None):
    if code:
        obj = Dictionary(code)
        data = obj.get_list()
        return vesta_jsonify(result=list(data))


def _get_fields(code):
    obj = Dictionary(code)
    document = list(obj.get_list(limit=1))
    if document[0]:
        return sorted(document[0].keys())
    return []
