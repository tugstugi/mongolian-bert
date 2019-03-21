#!/usr/bin/env python
"""Train a sentence piece model."""
__author__ = 'Erdene-Ochir Tuguldur'

import argparse
import sentencepiece as spm

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--vocab-size", type=int, default=32000, help='vocabulary size')
parser.add_argument("--control-symbols", type=str, default='[PAD],[CLS],[SEP],[MASK]', help='control symbols')
parser.add_argument("--prefix", type=str, default='mn_cased', help='model prefix')
parser.add_argument("--input", type=str, default='all.txt', help='input text file')
args = parser.parse_args()

print("training sentence piece...")
command = f'--input={args.input} --model_prefix={args.prefix} --vocab_size={args.vocab_size} ' \
          f'--control_symbols={args.control_symbols} --input_sentence_size=10000000 --shuffle_input_sentence=true '
spm.SentencePieceTrainer.Train(command)
print("done!")
