#!/usr/bin/env python3
"""Generate TFRecords for the max seq length 128 and 512 for a given model."""

import os
import sys
import glob
import argparse
from os.path import abspath, dirname, join, splitext, basename, exists


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("model_directory", type=str,
                    help='a model directory containing bert_config.json and the sentence piece models')
args = parser.parse_args()


SCRIPT_DIR = dirname(abspath(__file__))
PARENT_SCRIPT = join(SCRIPT_DIR, 'create_pretraining_data.py')
MN_CORPUS_FOLDER = 'mn_corpus'
MODEL_FILE = join(args.model_directory, 'mn_cased.model')
VOCAB_FILE = join(args.model_directory, 'mn_cased.vocab')

# check whether sentence piece models are existing
for f in [MODEL_FILE, VOCAB_FILE]:
    if not exists(f):
        print("'%s' doesn't exist!" % f)
        sys.exit(-1)


output_files = []
for input_file in sorted(glob.glob('%s/*.txt' % join(SCRIPT_DIR, MN_CORPUS_FOLDER))):
    input_file = abspath(input_file)
    for (max_seq, max_pred_per_seq) in [[128, 20], [512, 77]]:
        output_file = join(args.model_directory, 'maxseq%i-%s.tfrecord' % (max_seq, splitext(basename(input_file))[0]))
        output_files.append(output_file)

        command = """python3 %s \
--input_file=%s \
--output_file=%s \
--model_file=%s \
--vocab_file=%s \
--do_lower_case=False \
--max_seq_length=%i \
--max_predictions_per_seq=%i \
--masked_lm_prob=0.15 \
--random_seed=12345 \
--dupe_factor=5""" % (PARENT_SCRIPT, input_file, output_file, MODEL_FILE, VOCAB_FILE, max_seq, max_pred_per_seq)

        print(command)
        os.system(command)

print('done')
print('\n\n\n')
print('tf record files:\n')
print('export INPUT_FILES=%s' % ','.join(output_files))
