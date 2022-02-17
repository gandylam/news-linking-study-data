awk 'FNR > 1' export/links-by-media/csv/*.csv > export/links-by-media/links-consolidated.csv
cat export/links-by-media/link-csv-headers.txt export/links-by-media/links-consolidated.csv > export/links-by-media/links-all.csv
rm export/links-by-media/links-consolidated.csv
