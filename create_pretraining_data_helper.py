#!/usr/bin/env python3
"""Generate TFRecords for the max seq length 128 and 512 for a given model."""

import os
import sys
import glob
import argparse
from os.path import abspath, dirname, join, splitext, basename, exists


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--max_seq_length", type=int,
                    help='max_seq_length see BERT')
parser.add_argument("--max_predictions_per_seq", type=int,
                    help='max_predictions_per_seq see BERT')
parser.add_argument("--cased", action='store_true',
                    help='if set, create data using cased SentencePiece')
args = parser.parse_args()


SCRIPT_DIR = dirname(abspath(__file__))
PARENT_SCRIPT = join(SCRIPT_DIR, 'create_pretraining_data.py')
MN_CORPUS_FOLDER = 'mn_corpus'
sp_name = 'mn_cased' if args.cased else 'mn_uncased'
MODEL_FILE = 'sentencepiece/%s.model' % sp_name
VOCAB_FILE = 'sentencepiece/%s.vocab' % sp_name

# check whether sentence piece models are existing
for f in [MODEL_FILE, VOCAB_FILE]:
    if not exists(f):
        print("'%s' doesn't exist!" % f)
        sys.exit(-1)


output_files = []
for input_file in sorted(glob.glob('%s/*.txt' % join(SCRIPT_DIR, MN_CORPUS_FOLDER))):
    input_file = abspath(input_file)
    output_file = join(MN_CORPUS_FOLDER, 'maxseq%i-%s.tfrecord' % (args.max_seq_length, splitext(basename(input_file))[0]))
    output_files.append(output_file)

    command = """python3 %s \
--input_file=%s \
--output_file=%s \
--model_file=%s \
--vocab_file=%s \
--do_lower_case=%s \
--max_seq_length=%i \
--max_predictions_per_seq=%i \
--masked_lm_prob=0.15 \
--random_seed=12345 \
--dupe_factor=5""" % (PARENT_SCRIPT, input_file, output_file, MODEL_FILE, VOCAB_FILE,
                      'False' if args.cased else 'True',
                      args.max_seq_length, args.max_predictions_per_seq)
    print(command)
    os.system(command)

print('done')
print('\n\n\n')
print('tf record files %i :\n' % len(output_files))
output_files = ["gs://mongolian-bert/$MODEL_DIR/%s" % basename(f) for f in output_files]
print('export INPUT_FILES=%s' % ','.join(output_files))
