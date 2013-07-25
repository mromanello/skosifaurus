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

__version__ = (0,2)

class MARCXMLReader(object):
    """Returns the PyMARC record from the OAI structure for MARC XML"""
    def __call__(self, element):
        #print element[0][1].text
        handler = marcxml.XmlHandler()
        marcxml.parse_xml(StringIO(tostring(element[0], encoding='UTF-8')), handler)
        return handler.records[0]

def download_records(client=None,dest_dir="./raw/", oai_set=None, oai_metadataprefix=None,limit = 100,complete_harvest = False,save=False):
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
	"""docstring for load_records"""
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

def add_metadata(graph, n_marc_recs, n_proc_recs, n_triples, oai_endpoint,version=__version__):
	"""docstring for create_metadata"""
	pass

def to_RDF(records,base_namespace="http://http://zenon.dainst.org/thesaurus/",lang_codes=None):
	"""
	docstring for as_RDF
	"""
	from rdflib import Namespace, BNode, Literal, URIRef,RDF,RDFS
	from rdflib.graph import Graph, ConjunctiveGraph
	from rdflib.plugins.memory import IOMemory
	
	store = IOMemory()
	g = ConjunctiveGraph(store=store)
	skos = Namespace('http://www.w3.org/2004/02/skos/core#')
	base = Namespace(base_namespace)
	g.bind('skos',skos)
	g.bind('base',base)
	thesaurus = URIRef(base["thesaurus"])
	#g.add((thesaurus,RDF.type, skos["ConceptScheme"]))
	for n,record in enumerate(records):
		try:
			if(record is not None):
				uri = URIRef(base[record['id']])
				g.add((uri, RDF.type, skos['Concept']))
				g.add((uri,skos["inScheme"],thesaurus))
				if(record['broader_id'] is not None):
					g.add((uri,skos['broader'],URIRef(base[record['broader_id']])))
				else:
					g.add((uri,skos["topConceptOf"],thesaurus))
				if(record['hidden_label'] is not None):
					g.add((uri,skos["hiddenLabel"],Literal(record['hidden_label'])))
				if(record['labels'] is not None):
					for lang in record['labels'].keys():
						if(lang=="ger"):
							g.add((uri,skos["prefLabel"],Literal(record['labels'][lang],lang=lang_codes[lang])))
						else:
							g.add((uri,skos["altLabel"],Literal(record['labels'][lang],lang=lang_codes[lang])))
				if(record['anon_nodes'] is not None):
					for node_id,node in record['anon_nodes']:
						temp = URIRef(base[node_id])
						g.add((temp,RDF.type,skos['Concept']))
						g.add((temp,skos["prefLabel"],Literal(node)))
						g.add((temp,skos['broader'],uri))
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
	import sys
	dai_oaipmh = "http://opac.dainst.org/OAI"
	client = init_client(dai_oaipmh)
	#records = download_records(client=client,oai_set='DAI_THS',oai_metadataprefix='marc21',complete_harvest=True,save=True,limit=1000)
	records = load_records(dest_dir="/Users/rromanello/Documents/zenon-raw/")
	global lang_codes
	lang_codes = get_language_codes(filename="/Users/rromanello/Documents/skosifaurus/extra/lang_codes.data")
	for n,id in enumerate(records.keys()):
		out_f = codecs.open('%s%s.ttl'%('/Users/rromanello/Documents/skosifaurus/turtle/',id),'w','utf-8')
		try:
			temp  = process_pymarc_record(records[id])
			temp_rdf = to_RDF(temp,lang_codes=lang_codes)
			out_f.write(temp_rdf.serialize(format='turtle'))
			print >> sys.stderr, "Serialized to Turtle and saved record %i/%i"%(n,len(records.keys()))
			out_f.close()
		except Exception, e:
			#raise e
			print >> sys.stderr, "Error while serializing to Turtle and saving record %i. Error: \"%s\""%(n,e)
	return

if __name__ == '__main__':
	main()
