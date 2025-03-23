#!/usr/bin/env python3

from flask import Flask, request, render_template
import os
import sqlite3

base_dir = os.path.dirname(__file__)
app = Flask('treebank2curriculum',
            static_folder=os.path.join(base_dir, 'static'),
            static_url_path='/static',
            template_folder=os.path.join(base_dir, 'templates'))

@app.route('/', methods=['get', 'post'])
def main_page():
    freq = 500
    try:
        freq = int(request.form.get('freq', '500'))
    except:
        pass
    db_path = os.environ['T2C_DB']
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('SELECT key, name FROM features')
    feats = {}
    for row in cur.fetchall():
        feats[row[0]] = (request.form.get(row[0], '') == 'on', row[1])
    pos = [f for f in feats if feats[f][0]]
    neg = [f for f in feats if not feats[f][0]]
    if not pos:
        return render_template('index.html', feats=feats, sents=[],
                               freq=freq)
    sel = 'SELECT sentence FROM sentence_features WHERE feature = ?'
    query = ' UNION '.join([sel] * len(pos))
    query += ''.join([' EXCEPT '+sel] * len(neg))
    cur.execute(query, pos+neg)
    ids = [x[0] for x in cur.fetchall()]
    qs = ', '.join(['?']*len(ids))
    cur.execute(f'SELECT key, content FROM sentences WHERE key IN ({qs}) AND freq < ?',
                ids + [freq])
    sents = cur.fetchall()
    order = request.form.get('sort-order')
    if order == 'len':
        sents.sort(key=lambda x: len(x[1]))
    return render_template('index.html', feats=feats, sents=sents,
                           order=order, freq=freq)
