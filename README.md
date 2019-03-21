## Data preparation

Download the Mongolian Wikipedia and the 700 million word news data set and pre process them into a file `all.txt`:
```
# Mongolian Wikipedia
python dl_and_preprop_mn_wiki.py
# 700 million word news data set
python dl_and_preprop_mn_news.py
# concat the both into a big file
cat mn_wiki.txt mn_news_700m.txt > all.txt
```

## Train SentencePiece vocabulary

Now, train the SentencePiece model:
```
python train_sentencepiece.py --input all.txt --vocab-size 32000 --prefix mn_cased
```
If the training was successful, the following files should be created: `mn_cased.model` and `mn_cased.vocab`.
You can also test whether the SentencePiece model is working as intended:
```
>>> import sentencepiece as spm
>>> s = spm.SentencePieceProcessor()
>>> s.Load('mn_cased.model')
>>> s.EncodeAsPieces('Мөнгөө тушаачихсаныхаа дараа мэдэгдээрэй')
['▁Мөн', 'гөө', '▁тушаа', 'чихсан', 'ыхаа', '▁дараа', '▁мэдэгд', 'ээр', 'эй']
```
