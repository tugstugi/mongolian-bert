# Mongolian BERT models

This repository contains pre-trained Mongolian [BERT](https://arxiv.org/abs/1810.04805) models trained by [tugstugi](https://github.com/tugstugi), [enod](https://github.com/enod) and [sharavsambuu](https://github.com/sharavsambuu).
Special thanks to [nabar](https://github.com/nabar) who provided 5x TPUs.


This repository is based on the following open source projects: [google-research/bert](https://github.com/google-research/bert/),
[huggingface/pytorch-pretrained-BERT](https://github.com/huggingface/pytorch-pretrained-BERT) and [yoheikikuta/bert-japanese](https://github.com/yoheikikuta/bert-japanese).


## Models

[SentencePiece](https://github.com/google/sentencepiece) with a vocabulary size 32000 is used as the text tokenizer.
You can use the masked language model notebook
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tugstugi/mongolian-bert/blob/master/notebooks/MaskedLM.ipynb)
to test how good the pre-trained models could predict masked Mongolian words.

* cased BERT-Base: [TensorFlow checkpoint](https://drive.google.com/file/d/1MOZUKppfX45BEh7nxQ5AvzK-8wIUITr8) and [PyTorch model](https://drive.google.com/file/d/11Adpo6DorPgpE8z1lL6rvZAMHLEfnJwv)
* cased BERT-Large: to be released
* uncased BERT-Base: [TensorFlow checkpoint](https://drive.google.com/file/d/1t1r2lGn_7MncBBDcYZWykZndV-BcBJxX) and [PyTorch model](https://drive.google.com/file/d/1SnRKbLbwyRsDVCW34Li7zRrpmkKA1VVO)
* uncased BERT-Large: to be released

### Cased BERT-Base
Download either [TensorFlow checkpoint](https://drive.google.com/file/d/1MOZUKppfX45BEh7nxQ5AvzK-8wIUITr8) or
[PyTorch model](https://drive.google.com/file/d/11Adpo6DorPgpE8z1lL6rvZAMHLEfnJwv). Eval results:
```
global_step = 4000000
loss = 1.3476765
masked_lm_accuracy = 0.7069192
masked_lm_loss = 1.2822781
next_sentence_accuracy = 0.99875
next_sentence_loss = 0.0038988923
```

### Uncased BERT-Base
Download either [TensorFlow checkpoint](https://drive.google.com/file/d/1t1r2lGn_7MncBBDcYZWykZndV-BcBJxX) or
[PyTorch model](https://drive.google.com/file/d/1SnRKbLbwyRsDVCW34Li7zRrpmkKA1VVO). Eval results:
```
global_step = 4000000
loss = 1.3115116
masked_lm_accuracy = 0.7018335
masked_lm_loss = 1.3155857
next_sentence_accuracy = 0.995
next_sentence_loss = 0.015816934
```


## Finetuning

To be released.

Finetuning for Mongolian text classification will be released in
[sharavsambuu/mongolian-text-classification](https://github.com/sharavsambuu/mongolian-text-classification).

## Pre-Training

This repo already provides pre-trained models. If you really want to pre-train from scratch, you will need a TPU.
A base model can be trained in 13 days (4M steps) on TPUv2. For a big model, you will need more than a month.
We have used `max_seq_length=512` instead of training first with `max_seq_length=128` and then with `max_seq_length=512`
because it had better masked LM accuracy.

### Install

Checkout the project and install dependencies:
```
git clone --recursive https://github.com/tugstugi/mongolian-bert.git
pip3 install -r requirements.txt
```

### Data preparation

Download the Mongolian Wikipedia and the 700 million word Mongolian news data set and pre process them into the directory `mn_corpus/`:
```
# Mongolian Wikipedia
python3 datasets/dl_and_preprop_mn_wiki.py
# 700 million words Mongolian news data set
python3 datasets/dl_and_preprop_mn_news.py
```
After pre-processing, the dataset will contain around 500M words.

### Train SentencePiece vocabulary

Now, train the cased SentencePiece model i.e. with the vocabulary size 32000 :
```
cd sentencepiece
cat ../mn_corpus/*.txt > all.txt
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
For a uncased SentencePiece model, convert the content of `all.txt` to lower case and train with:
```
python3 train_sentencepiece.py --input all.txt --vocab-size 32000 --prefix mn_uncased
```

### Create/Upload TFRecord files
Create TFRecord files for cased:
```
python3 create_pretraining_data_helper.py --max_seq_length=512 --max_predictions_per_seq=77 --cased
```
Upload to your GCloud bucket:
```
gsutil cp mn_corpus/maxseq512*.tfrecord gs://YOUR_BUCKET/data-cased/
```
For uncased, adjust above steps accordingly.

### Train a model
To train, i.e. uncased BERT-Base on TPUv2, use the following command:
```
export INPUT_FILES=gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_1.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_10.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_11.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_12.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_13.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_14.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_15.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_16.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_17.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_18.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_19.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_2.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_3.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_4.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_5.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_6.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_7.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_8.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_news_700m_9.tfrecord,gs://YOUR_BUCKET/data-uncased/maxseq512-mn_wiki.tfrecord
python3 bert/run_pretraining.py \
  --input_file=$INPUT_FILES \
  --output_dir=gs://YOUR_BUCKET/uncased_bert_base \
  --use_tpu=True \
  --tpu_name=YOUR_TPU_ADDRESS \
  --num_tpu_cores=8 \
  --do_train=True \
  --do_eval=True \
  --bert_config_file=bert_configs/bert_base_config.json \
  --train_batch_size=256 \
  --max_seq_length=128 \
  --max_predictions_per_seq=20 \
  --num_train_steps=4000000 \
  --num_warmup_steps=10000 \
  --learning_rate=1e-4
```
For a large model, use `bert_config_file=bert_configs/bert_large_config.json` and `train_batch_size=32`.

### Citation
```
@misc{mongolian-bert,
  author = {Tuguldur, Erdene-Ochir and Gunchinish, Sharavsambuu and Bataa, Enkhbold},
  title = {BERT Pretrained Models on Mongolian Datasets},
  year = {2019},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/tugstugi/mongolian-bert/}}
}
```