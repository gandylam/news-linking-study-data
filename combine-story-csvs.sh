awk 'FNR > 1' export/stories-by-media/*.csv > export/stories-consolidated.csv
cat export/story-csv-headers.txt export/stories-consolidated.csv > export/stories-all.csv
rm export/stories-consolidated.csv
