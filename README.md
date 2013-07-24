# SKOSifaurus

dependencies:

* pyoai
* pymarc
* rdflib

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