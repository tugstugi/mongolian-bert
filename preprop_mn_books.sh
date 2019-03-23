#!/bin/bash

mkdir -p ebooks/

for file in ebooks/*
do
  if [ "${file##*.}" == "epub" ]; then
    python bookextractor/epub.py $(pwd)/"$file"
  elif [ "${file##*.}" == "mobi" ]; then
    python bookextractor/mobi.py $(pwd)/"$file"
  fi
done
