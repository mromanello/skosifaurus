# Skosifaurus

These are the steps performed:

1. Run the python script
	
	python harvest_marc.py 	# this generates the file thesaurus.csv as output
	
2. From within the StellarConsole (which runs exclusively on Windows) run

	csv2rdf /csv:"thesaurus.csv" /template:SKOS_CONCEPTS /ns:"http://data.dainst.de/zenon/" /rdf:"thesaurus.csv.rdf"
	
Step #2 will write the RDF output to the specified file.