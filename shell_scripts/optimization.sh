#!/bin/sh

for QNAME in bull davis_southern_women diamond hoffman_singleton house_x les_miserables qh882 tutte
do
  poetry run python optimization.py $QNAME stress 100 &&
done

say 'hello'
