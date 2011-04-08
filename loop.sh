#!/bin/bash

while [ 1 ]
do
  date
  python scrape.py
  if [ $? -eq 0 ]; then
    sleep 300;
  else
    sleep 30;
  fi
done
