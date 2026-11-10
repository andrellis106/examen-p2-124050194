#!/bin/bash
set -e

OUT=/data/output/resultado

# Hadoop exige que la carpeta de salida NO exista
rm -rf "$OUT"

time hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input /data/input/ventas_124050194.csv \
  -output "$OUT" \
  -mapper "python3 /app/mapreduce/mapper.py" \
  -reducer "python3 /app/mapreduce/reducer.py"