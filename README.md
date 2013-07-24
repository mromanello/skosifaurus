# SKOSifaurus

This repository contains a SKOS/RDF version of the thesaurus underlying [Zenon](http://de.wikipedia.org/wiki/ZENON), the OPAC of the [German Archaeological Institute](http://www.dainst.org/), as well as the code used to produce it. The thesaurus is created by harvesting about 80k Marc21 XML records from [DAI's OAI-PMH interface](http://opac.dainst.org/OAI) that are then transformed into SKOS/RDF format. The thesaurus currently contains 135,916 SKOS concepts for a total of 817,900 triples. 

## Installation

The following dependencies need to be pre-installed:

* pyoai
* pymarc
* rdflib

## Get Started

To be finished...

<!--

SKOSifaurus can either run as script or be used as library.

	import __init__
	form __init__ import *
	client = init_client()
	zenon_raw = "./turtle/"
	zenon_ttl = "./raw/"
	lang_codes = get_language_codes("./extra/lang_codes.data")
	records = download_records(dest_dir=zenon_raw,client=client,oai_set='DAI_THS',oai_metadataprefix='marc21',complete_harvest=False,save=True,limit=1000)
	proc_recs = [process_pymarc_record(records[id]) for id in records.keys()]
	graph = to_RDF(proc_recs,lang_codes=lang_codes)
	print graph.serialize(format="turtle")
	hist
-->