#!/bin/bash

. venv/bin/activate
PYTHONPATH="/home/daniel/treebank2curriculum/blocks/:$PYTHONPATH"
export PYTHONPATH
cat ~/hbo-UD/UD_Ancient_Hebrew-PTNK/*.conllu | udapy util.Filter keep_tree="'$1-$2:' in tree.sent_id" .Simplify level=$3
