## Install

Checkout the project and install dependencies:
```
git clone --recursive https://github.com/tugstugi/mongolian-bert.git
pip3 install -r requirements.txt
```


## Data preparation

Download the Mongolian Wikipedia and the 700 million word Mongolian news data set and pre process them into a directory `mn_corpus/`:
(download already prepared file from [here](https://www.dropbox.com/s/s1eweex28t6trqj/all.txt.gz?dl=1))
```
# Mongolian Wikipedia
python3 dl_and_preprop_mn_wiki.py
# 700 million words Mongolian news data set
python3 dl_and_preprop_mn_news.py
```

## Train SentencePiece vocabulary

Now, train the SentencePiece model (repo contains already a trained model):
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


## TODO:
* SentencePiece unigram or BPE?
* vocabulary size bigger than 32000? Mongolian language has 85K root words.
* BERT max_seq_length 128 or longer?
* cased is probably better...
* ...
