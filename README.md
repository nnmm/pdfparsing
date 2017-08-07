# Usage

First, install the pdfquery library:

	pip3 install pdfquery

Then run

	python3 extract.py --header "MwSt" --cols Anzahl Bezeichnung - - Preis -- FILE

where FILE is the pdf to extract data from. The arguments after "cols" have to correspond to the columns of the table. "-" means that the column is ignored. The other possible column values are "Anzahl", "Bezeichnung" and "Preis". Note that it's necessary to put "--" before the file name to separate it from the columns.

The script prints the columns that have been specified to the console. See also

	python3 extract.py -h

for help.

On Windows, it's probably 'pip3.exe' and python3.exe' instead.