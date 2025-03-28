#!/usr/bin/env python3

import argparse
import collections
import json
import os
import sqlite3
import subprocess
import tempfile
import tomllib

parser = argparse.ArgumentParser('Compile sentence database')
parser.add_argument('db', help='Database file')
parser.add_argument('queries', help='TOML file of feature queries')
parser.add_argument('trees', nargs='+', help='CoNLL-U files')
args = parser.parse_args()

try:
    os.remove(args.db)
except:
    pass

con = sqlite3.connect(args.db)
cur = con.cursor()

con.executescript('''
CREATE TABLE features(key TEXT, name TEXT);
CREATE TABLE sentences(key TEXT, content TEXT, freq INTEGER);
CREATE TABLE sentence_features(feature TEXT, sentence TEXT);
''')

run_args = ['grew', 'grep']

freq = collections.Counter()
sents = []
for fname in args.trees:
    run_args += ['-i', fname]
    with open(fname) as fin:
        for block in fin.read().split('\n\n'):
            sid = None
            text = None
            lemmas = set()
            for line in block.splitlines():
                if line.startswith('# sent_id = '):
                    sid = line.split('=', 1)[1].strip()
                elif line.startswith('# text = '):
                    text = line.split('=', 1)[1].strip()
                elif '\t' in line and 'PUNCT' not in line:
                    lm = line.split('\t')[2]
                    if lm != '_':
                        lemmas.add(lm)
                        freq[lm] += 1
            if sid and text:
                sents.append((sid, text, lemmas))

rank = {lemma: rank for rank, (lemma, freq) in enumerate(freq.most_common())}
for sid, text, lemmas in sents:
    cur.execute(
        'INSERT INTO sentences(key, content, freq) VALUES(?, ?, ?)',
        [sid, text, max([rank[lm] for lm in lemmas])],
    )

con.commit()

with open(args.queries, 'rb') as fin, tempfile.NamedTemporaryFile() as fquery:
    data = tomllib.load(fin)
    run_args += ['-request', fquery.name]
    for query in data['features']:
        fquery.seek(0)
        fquery.write(query['query'].encode('utf-8'))
        fquery.truncate()
        fquery.flush()
        proc = subprocess.run(run_args, capture_output=True,
                              encoding='utf-8')
        blob = json.loads(proc.stdout)
        sents = set([x['sent_id'] for x in blob])
        print(f'Found {len(sents)} sentences with {query["key"]}')
        cur.execute('INSERT INTO features(key, name) VALUES(?, ?)',
                    [query['key'], query['name']])
        cur.executemany(
            'INSERT INTO sentence_features(feature, sentence) VALUES(?, ?)',
            [(query['key'], s) for s in sents],
        )
        con.commit()
