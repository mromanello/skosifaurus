"""
Harvest MARC records via OAI-PMH.
"""


#Mostly from - http://code.google.com/p/oldmapsonline/source/browse/trunk/oai-pmh/oaipmh-client-pyoai-pymarc.py
# MarcXML reader - parsing done by pymarc

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


def process_pymarc_record(MARC_record):
	"""
	MARC_record is of type pymarc.record.Record
	"""
	dict_obj = {}
	labels = {}
	
	# get the labels
	for field in MARC_record.get_fields('551'):
	    labels[field['9']] = field['a']
	dict_obj["labels"] = labels
	
	# get the id
	dict_obj["id"] = MARC_record.get_fields('001')[0].value()
	
	# get the id of the broader term/concept
	try:
		dict_obj["broader_id"] = MARC_record.get_fields('554')[0]['b']
	except Exception, e:
		dict_obj["broader_id"] = ""
	
	
	try:
		dict_obj["related_id"] = MARC_record['557']['1']
	except Exception, e:
		dict_obj["related_id"] = ""

	print dict_obj
	return dict_obj

def as_csv(dict_obj,header=False):
	# depends on how many labels there are
	lines = []
	if(header):
		columns = ["concept_id","broader_id","related_id","language","preflabel","altlabel","hiddenlabel",]
		lines.append(",".join(["\"%s\""%key for key in columns]))
	# output labels
	for label in dict_obj["labels"]:
		if(label == "ger"):
			tmp = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\""%(dict_obj["id"],"","",label, dict_obj["labels"][label],"","")
			lines.append(tmp)
		else:
			tmp = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\""%(dict_obj["id"],"","",label,"",dict_obj["labels"][label],"")
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

limit = 500
records = []

print>>sys.stderr, 'beginning harvest'
 
output = []
for count, rec in enumerate(recs):
	if(count < limit):
		id = rec[0].identifier()
		records.append(rec)
		print>>sys.stderr, "harvested record %i"%(count+1)
		obj = process_pymarc_record(rec[1])
		if(count == 0):
			output += as_csv(obj,True)
		else:
			output += as_csv(obj,False)
	else:
		break
		
import codecs
file = codecs.open("thesaurus.csv","w","utf-8-sig")
file.write("\n".join(output))
file.close()	