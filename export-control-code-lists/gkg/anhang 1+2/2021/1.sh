sed -Ee 's/^"?([^,"]*)"?,("?)(([a-z]\))|([0-9]\.))/"\1\3",\2/' de.csv
