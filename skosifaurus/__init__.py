"""
Harvest MARC records via OAI-PMH.
"""

#Handle utf-8 strings
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from lxml import etree
import hashlib

from cStringIO import StringIO
from lxml.etree import tostring
from pymarc import marcxml, MARCWriter, field

__version__ = (0,3)

class MARCXMLReader(object):
    """Returns the PyMARC record from the OAI structure for MARC XML"""
    def __call__(self, element):
        #print element[0][1].text
        handler = marcxml.XmlHandler()
        marcxml.parse_xml(StringIO(tostring(element[0], encoding='UTF-8')), handler)
        return handler.records[0]

def download_records(client=None, dest_dir="./raw/", oai_set=None, oai_metadataprefix=None, limit = 100, complete_harvest = False, save=False):
	"""
	TODO
	"""
	import pickle
	records = client.listRecords(metadataPrefix=oai_metadataprefix, set=oai_set)
	result = {}
	for count, record in enumerate(records):
		if(count < limit or complete_harvest is True):
			print >> sys.stderr,"Downloading and saving record %i"%count
			result[record[0].identifier()] = record[1]
			if(save):
				try:
					fname = '%s%s.pickle'%(dest_dir,record[0].identifier())
					pickle.dump(record[1],open(fname,'w'))
				except Exception, e:
					#print >> sys.stderr, "there was problem with writing %s"%'%s%s.json'%(dest_dir,record[0].identifier())
					print e
		else:
			break
	return result

def load_records(dest_dir="./raw/",limit=None):
	"""
	docstring for load_records
	"""
	import os
	import pickle
	records = {}
	if(dir is not None):
		files = ["%s%s"%(dest_dir,file) for file in os.listdir(dest_dir) if file.endswith(".pickle")]
		if(limit is not None):
			files= files[:limit]
		for n,fname in enumerate(files):
			try:
				temp = pickle.load(open(fname,'r'))
				id=process_pymarc_record(temp)["id"]
				records[id]=temp
				print >> sys.stderr, "Loaded record %i/%i"%(n,len(files))
			except Exception, e:
				print >> sys.stderr, "Error while reading record %i. Error: \"%s\""%(n,e)
	return records

def init_client(oai_baseurl="http://opac.dainst.org/OAI"):
	"""docstring for init_client"""
	from oaipmh import metadata
	from oaipmh.client import Client
	from oaipmh.metadata import MetadataRegistry
	
	marcxml_reader = MARCXMLReader()
	registry = metadata.MetadataRegistry()
	registry.registerReader('marc21', marcxml_reader)
	client = Client(oai_baseurl, registry)
	return client

def get_language_codes(filename="extra/lang_codes.data"):
	"""
	reads a language code table from an external file and creates
	a dictionary out of it, for the sake of easy look-ups.
	The original table file was downloaded from <http://loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt>
	The returns this dictionary.
	"""
	
	import pickle
	codes = pickle.load(open(filename,'r'))
	return codes

def process_pymarc_record(MARC_record):
	"""
	MARC_record is of type pymarc.record.Record
	
	TODO
		* add hidden_label (553.a)
		* 552.r => narrower term (lang unknown, id to be assigned automatically)
	
	"""
	dict_obj = {}
	labels = {}
	dict_obj["anon_nodes"] = []
	if(MARC_record is not None):
		try:
			# get the labels
			for field in MARC_record.get_fields('551'):
			    labels[field['9']] = field['a']
			dict_obj["labels"] = labels
		except Exception, e:
			dict_obj["labels"] = None
	
		# get the id
		dict_obj["id"] = MARC_record.get_fields('001')[0].value()
	
		# get the id of the broader term/concept
		try:
			dict_obj["broader_id"] = MARC_record.get_fields('554')[0]['b']
		except Exception, e:
			dict_obj["broader_id"] = None
		try:
			dict_obj["hidden_label"] = MARC_record.get_fields('553')[0]['a']
		except Exception, e:
			dict_obj["hidden_label"] = None
		try:
			# needs to be subfield 'b'
			dict_obj["related_id"] = MARC_record['557']['1']
		except Exception, e:
			dict_obj["related_id"] = None
			
		try:
			items = MARC_record.get_fields('552')
			# TODO handle not only 'r' fields, but also 'm' and 'e'
			m = hashlib.md5()
			for item in items:
				if(item['r'] is not None):
					m.update(item['r'])
					dict_obj["anon_nodes"].append(("%s_%s"%(dict_obj["id"],m.hexdigest()),item['r']))
				elif(item['m'] is not None):
					m.update(item['m'])
					dict_obj["anon_nodes"].append(("%s_%s"%(dict_obj["id"],m.hexdigest()),item['m']))
				elif(item['e'] is not None):
					m.update(item['e'])
					dict_obj["anon_nodes"].append(("%s_%s"%(dict_obj["id"],m.hexdigest()),item['e']))
		except Exception, e:
			raise e	
			
		return dict_obj
	else:
		return None

def add_metadata(graph, n_marc_recs, n_processed_records, n_triples, oai_endpoint,version=__version__,base_namespace="http://zenon.dainst.org/"):
	"""docstring for create_metadata"""
	from rdflib import Namespace, BNode, Literal, URIRef,RDF,RDFS
	from rdflib.graph import Graph, ConjunctiveGraph
	from rdflib.plugins.memory import IOMemory
	import datetime
	base = Namespace(base_namespace)
	dc = Namespace('http://purl.org/dc/elements/1.1/')
	graph.bind('dc',dc)
	thesaurus = URIRef(base["thesaurus"])
	license = URIRef("http://www.gnu.org/licenses/gpl.html")
	graph.add((thesaurus,dc["title"], Literal("The Thesaurus of the German Archaeological Institute in SKOS/RDF format.",lang="en")))
	graph.add((thesaurus,dc["creator"], Literal("SKOSifaurus <https://github.com/mromanello/skosifaurus> v. %s"%(".".join([str(n) for n in version])),lang="en")))
	graph.add((thesaurus,dc["date"],Literal(str(datetime.datetime.now()))))
	graph.add((thesaurus,dc["license"],license))
	graph.add((license,RDFS.label,Literal("GNU General Public License",lang="en")))
	graph.add((thesaurus,dc["source"],URIRef("http://zenon.dainst.org/")))
	graph.add((thesaurus,dc["description"],Literal("This serialization of the Zenon thesaurus was created by harvesting the OAI-PMH end-point (\"%s\"). Out of the %i Marc21 XML records available, %i were parsed without errors and transformed into %i triples."%(oai_endpoint,n_marc_recs,n_processed_records,n_triples),lang="en")))
	return graph

def to_RDF(records,base_namespace="http://zenon.dainst.org/",lang_codes=None,skosxl=False):
	"""
	docstring for as_RDF
	"""
	from rdflib import Namespace, BNode, Literal, URIRef,RDF,RDFS
	from rdflib.graph import Graph, ConjunctiveGraph
	from rdflib.plugins.memory import IOMemory
	
	store = IOMemory()
	g = ConjunctiveGraph(store=store)
	skos = Namespace('http://www.w3.org/2004/02/skos/core#')
	skosxl = Namespace('http://www.w3.org/2008/05/skos-xl#')
	base = Namespace(base_namespace)
	g.bind('skos',skos)
	g.bind('skosxl',skosxl)
	g.bind('base',base)
	thesaurus = URIRef(base["thesaurus"])
	g.add((thesaurus,RDF.type, skos["ConceptScheme"]))
	for n,record in enumerate(records):
		label_counter = 1
		try:
			if(record is not None):
				uri = URIRef(base[record['id']])
				g.add((uri, RDF.type, skos['Concept']))
				g.add((uri,skos["inScheme"],thesaurus))
				if(record['broader_id'] is not None):
					g.add((uri,skos['broader'],URIRef(base[record['broader_id']])))
					g.add((URIRef(base[record['broader_id']]),skos['narrower'],uri))
				else:
					g.add((uri,skos["topConceptOf"],thesaurus))
				if(record['hidden_label'] is not None):
					if(skosxl):
						label_uri = URIRef("%s#l%i"%(base[record['id']],label_counter))
						g.add((label_uri,RDF.type,skosxl["Label"]))
						g.add((label_uri,skosxl["literalForm"],Literal(record['hidden_label'])))
						g.add((uri,skosxl["hiddenLabel"],label_uri))
						label_counter += 1
					else:
						g.add((uri,skos["hiddenLabel"],Literal(record['hidden_label'])))
				if(record['labels'] is not None):
					for lang in record['labels'].keys():
						if(skosxl):
							label_uri = URIRef("%s#l%i"%(base[record['id']],label_counter))
							g.add((label_uri,RDF.type,skosxl["Label"]))
							g.add((label_uri,skosxl["literalForm"],Literal(record['labels'][lang],lang=lang_codes[lang])))
							g.add((uri,skosxl["prefLabel"],label_uri))
							label_counter += 1
						else:
							g.add((uri,skos["prefLabel"],Literal(record['labels'][lang],lang=lang_codes[lang])))
				if(record['anon_nodes'] is not None):
					for node_id,node in record['anon_nodes']:
						temp = URIRef(base[node_id])
						g.add((temp,RDF.type,skos['Concept']))
						g.add((temp,skos["inScheme"],thesaurus))
						g.add((temp,skos['broader'],uri))
						if(skosxl):
							label_uri = URIRef("%s#l%i"%(base[node_id],label_counter))
							g.add((label_uri,RDF.type,skosxl["Label"]))
							g.add((label_uri,skosxl["literalForm"],Literal(node,lang="de")))
							g.add((temp,skosxl["prefLabel"],label_uri))
							label_counter += 1
						else:
							g.add((temp,skos["prefLabel"],Literal(node,lang="de")))
				print >> sys.stderr, "Record %s converted into RDF (%i/%i)"%(record['id'],n,len(records))
		except Exception, e:
			print >> sys.stderr, "Failed converting record %s with error %s (%i/%i)"%(record['id'],str(e),n,len(records))
	return g

def from_RDF(inp_dir=None,format=("turtle",".ttl")):
	"""docstring for from_RDF"""
	from rdflib.graph import Graph, ConjunctiveGraph
	from rdflib.plugins.memory import IOMemory
	import os
	store = IOMemory()
	g = ConjunctiveGraph(store=store)
	files = ["%s%s"%(inp_dir,file) for file in os.listdir(inp_dir) if file.endswith(format[1])]
        size = len(files)
	for n,f in enumerate(files):
		try:
			g.parse(f,format=format[0])
			print >> sys.stderr,"Read triples from file %s (%i/%i)"%(f,n,size)
		except Exception, e:
                    print e
			#print >> sys.stderr,"Failed reading triples from file %s, %s"%(f,str(e))
	return g

def main():
	"""docstring for main"""
	import argparse
	dai_oaipmh = "http://opac.dainst.org/OAI"
	parser = argparse.ArgumentParser(prog="skosifaurus",description='SKOSify DAI\'s Zenon thesaurus.')
	parser.add_argument('-d','--download', action="store", dest="download_dir", default=None, help="when a path is specified, data is harvested directly from the oai-pmh interface and saved there")
	parser.add_argument('-l','--load', action="store", dest="load_dir", type=str,default=None, help="the directory containing the marc21xml records of the thesaurus")
	parser.add_argument('-m','--max', action="store", dest="limit", type=int, default=None,help="limit the process to the first n records")
	parser.add_argument('-o','--output', action="store", dest="outp_file", type=str, default=None,help="path of the output file")
	parser.add_argument('-f','--format', action="store", dest="outp_format", type=str, default=None,help="output format. accepted values are: turtle, xml")
	parser.add_argument('-x','--skos-xl', action="store_true", dest="skosxl", help="if this flag is passed, the output will be SKOS-XL compliant")
	parser.add_argument('-b','--base-uri', action="store", dest="base_uri", type=str, default=None,help="the base URI of the resulting SKOS/RDF thesaurus. Default is %s"%"http://http://zenon.dainst.org/thesaurus/")
	args = parser.parse_args()
	if ((args.download_dir is not None or args.load_dir is not None) and args.outp_file is not None and args.outp_format is not None):
		client = init_client(dai_oaipmh)
		processed_records = None
		records = None
		if args.download_dir is not None:
			lang_codes = get_language_codes(filename="./extra/lang_codes.data")
			if args.limit is None:
				records = download_records(client=client,oai_set='dai-ths',oai_metadataprefix='marc21',complete_harvest=True,save=True,dest_dir=args.download_dir)
			else:
				records = download_records(client=client,oai_set='dai-ths',oai_metadataprefix='marc21',limit=args.limit,save=True,dest_dir=args.download_dir)
		else:
			lang_codes = get_language_codes(filename="./extra/lang_codes.data")
			if args.limit is not None:
				records = load_records(dest_dir=args.load_dir,limit=args.limit)
			else:
				records = load_records(dest_dir=args.load_dir)
		processed_records = [process_pymarc_record(records[id]) for id in records.keys()]
		try:
			graph = to_RDF(processed_records,lang_codes=lang_codes,skosxl=args.skosxl)
			graph = add_metadata(graph,len(records),len(processed_records),len(graph),dai_oaipmh)
			graph.serialize(args.outp_file, format=args.outp_format)
			print >> sys.stderr, "Serialized %i triples to file %s"%(len(graph),args.outp_file)
		except Exception, e:
			raise e
	else:
		parser.print_help()
	return

if __name__ == '__main__':
	main()
