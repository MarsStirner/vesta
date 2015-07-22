# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname('..'))

from app.lib.lpu.data import connection, LPU_Data, MetaData, engine

meta = MetaData(engine)
meta.reflect(bind=engine, views=False,
             only=['rbPspdDocumentClass', 'rbPspdDocumentType', 'rbPspdDocumentField'])

obj = LPU_Data()
obj.import_lpu_dictionaries(meta.tables)


def autogen_pspd():
    import os
    with connection as c1, connection as c2:
        res = c1.execute("""SELECT code, name FROM rbPspdDocumentType WHERE class_code NOT IN('cmi', 'id', 'vmi', 'uniq') """)
        for tcode, tname in res:
            for code, name in (('serial', u'Серия'), ('number', u'Номер'), ('beg_date', u'Дата начала'), ('end_date', u'Дата окончания'), ('origin', u'Выдан'), ('text', u'Текст')):
                c2.execute(
                    """INSERT INTO rbPspdDocumentField (`oid`, `name`, `code`, `type_code`, `regexp`, `mask`) VALUES (%s, %s, %s, %s, '', '')""",
                    (os.urandom(10).encode('hex'), name, code, tcode))


