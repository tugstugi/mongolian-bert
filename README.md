## Install

Checkout the project and install dependencies:
```
git clone --recursive https://github.com/tugstugi/mongolian-bert.git
pip3 install -r requirements.txt
```


## Data preparation

Download the Mongolian Wikipedia and the 700 million word Mongolian news data set and pre process them into a directory `mn_corpus/`:
(you can also download it from [here](https://www.dropbox.com/s/l4wldeuyzi0x26k/mn_corpus.tar.gz?dl=1))
```
# Mongolian Wikipedia
python3 dl_and_preprop_mn_wiki.py
# 700 million words Mongolian news data set
python3 dl_and_preprop_mn_news.py
```

## Train SentencePiece vocabulary

Now, train the SentencePiece model i.e. with the vocabulary size 32000 :
```
cat mn_corpus/*.txt > all.txt
python3 train_sentencepiece.py --input all.txt --vocab-size 32000 --prefix mn_cased
```
If the training was successful, the following files should be created: `mn_cased.model` and `mn_cased.vocab`.
You can also test whether the SentencePiece model is working as intended:
```
>>> import sentencepiece as spm
>>> s = spm.SentencePieceProcessor()
>>> s.Load('mn_cased.model')
>>> s.EncodeAsPieces('Мөнгөө тушаачихсаныхаа дараа мэдэгдээрэй')
['▁Мөнгөө', '▁тушаа', 'чихсан', 'ыхаа', '▁дараа', '▁мэдэгд', 'ээрэй']
```

## Training
We are going to make multiple experiments, so we need some conventions.
* each experiment got its own gcloud bucket i.e. `mongolian-bert-32k-512` for vocabulary size 32000 and max_seq_length of 512.
* each model got its own directory i.e. `model-32k` for a base model with a vocabulary size of 32000 and contains
  * `bert_config.json` with `vocab_size` same as the SentencePiece vocabulary size
  * `mn_cased.model` and `mn_cased.vocab`


## TODO:
* SentencePiece unigram or BPE?
* vocabulary size bigger than 32000? Mongolian language has 85K root words.
  * english cased: 28996
  * multi lingual cased: 119547 `[PAD][UNK][CLS][SEP][MASK]<S><T>`
  * japanese uncased: 32000 `[PAD][CLS][SEP][MASK]`
* BERT max_seq_length 128 or longer?
  * `max_predictions_per_seq=max_seq_length * masked_lm_prob`
* cased is probably better...
* ...
