"""
Harvest MARC records via OAI-PMH.
"""

#Handle utf-8 strings
import codecs, sys
reload(sys)
sys.setdefaultencoding('utf-8')

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry
from lxml import etree

from cStringIO import StringIO
from lxml.etree import tostring
from pymarc import marcxml, MARCWriter, field
import sys

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
	if(MARC_record is not None):
		try:
			# get the labels
			for field in MARC_record.get_fields('551'):
			    labels[field['9']] = field['a']
			dict_obj["labels"] = labels
		except Exception, e:
			dict_obj["labels"] = []
	
		# get the id
		dict_obj["id"] = MARC_record.get_fields('001')[0].value()
	
		# get the id of the broader term/concept
		try:
			dict_obj["broader_id"] = MARC_record.get_fields('554')[0]['b']
		except Exception, e:
			dict_obj["broader_id"] = ""
		try:
			# needs to be subfield 'b'
			dict_obj["related_id"] = MARC_record['557']['1']
		except Exception, e:
			dict_obj["related_id"] = ""
		print dict_obj
		return dict_obj
	else:
		return None
	

def as_csv(dict_obj,header=False):
	# depends on how many labels there are
	lines = []
	if(header):
		columns = ["concept_id","broader_id","related_id","language","preflabel","altlabel","hiddenlabel",]
		lines.append(",".join(["\"%s\""%key for key in columns]))
	# output labels
	for label in dict_obj["labels"]:
		try:
			# replace the Marc21 lang code with the RDF-compliant one (won't validate otherwise)
			new_label = lang_codes[label]
		except Exception, e:
			new_label = label
		if(label == "ger"):
			tmp = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\""%(dict_obj["id"],"","",new_label, dict_obj["labels"][label],"","")
			lines.append(tmp)
		else:
			tmp = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\""%(dict_obj["id"],"","",new_label,"",dict_obj["labels"][label],"")
			lines.append(tmp)
	if(dict_obj["broader_id"] != "" or dict_obj["related_id"] !=""):
		tmp = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\""%(dict_obj["id"],dict_obj["broader_id"],dict_obj["related_id"],"","","","")
		lines.append(tmp)
	
	return lines

class MARCXMLReader(object):
    """Returns the PyMARC record from the OAI structure for MARC XML"""
    def __call__(self, element):
        #print element[0][1].text
        handler = marcxml.XmlHandler()
        marcxml.parse_xml(StringIO(tostring(element[0], encoding='UTF-8')), handler)
        return handler.records[0]

	
marcxml_reader = MARCXMLReader()

# Defining of metadata Readers in the Registry

from oaipmh import metadata

registry = metadata.MetadataRegistry()
registry.registerReader('marc21', marcxml_reader)

#### OAI-PMH Client processing 

URL = "http://opac.dainst.org/OAI"
oai = Client(URL, registry)

set_name = "DAI_THS"

recs = oai.listRecords(metadataPrefix='marc21',
                       set=set_name)
complete_harvest = True
limit = 5000
records = []

print>>sys.stderr, 'beginning harvest'

global lang_codes
lang_codes = get_language_codes()
 
output = []
for count, rec in enumerate(recs):
	if(count < limit or complete_harvest is True):
		id = rec[0].identifier()
		records.append(rec)
		print>>sys.stderr, "harvested record %i"%(count+1)
		obj = process_pymarc_record(rec[1])
		if(obj is not None):
			if(count == 0):
				output += as_csv(obj,True)
			else:
				output += as_csv(obj,False)
		else:
			print>>sys.stderr, "record %i is empty"%(count+1)
	else:
		break
		
import codecs
# utf-8-sig is essential otherwise the file won't be read as UTF-8 by the StellarConsole in Win environment
file = codecs.open("thesaurus.csv","w","utf-8-sig") 
file.write("\n".join(output))
file.close()	