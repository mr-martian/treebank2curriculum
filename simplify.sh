#!/bin/bash

TB_DIR=UD_Ancient_Hebrew-PTNK

book="$1"
chapter="$2"
level="$3"

. venv/bin/activate
PYTHONPATH="$(pwd)/blocks/:$PYTHONPATH"
export PYTHONPATH
cat $TB_DIR/*.conllu | udapy util.Filter keep_tree="'${book}-${chapter}:' in tree.sent_id" .Simplify level="$level"
