
## Software

* [the CAA paper](https://www.ocs.soton.ac.uk/index.php/CAA/2012/paper/view/577)
* [STELLAR Console](http://reswin1.isd.glam.ac.uk/stellar/STELLAR.Setup.msi)
	* and related [tutorial](http://reswin1.isd.glam.ac.uk/stellar/tutorials/tutorial1.html)
*  "C:\Users\mro\Dropbox\DAI-DARIAH\DARIAH\AP3\use_case_zenon\tutorial_data\"

## Information about Zenon data (from Sabine Thaenert)

Data sources:

1. Archäologische Bibliographie:
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000004309&metadataPrefix=marc21
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000004209&metadataPrefix=marc21
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000004319&metadataPrefix=marc21
	* 	http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000003519&metadataPrefix=marc21
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000003719&metadataPrefix=marc21
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000002119&metadataPrefix=marc21

2. Iberische Halbinsel:
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000000019&metadataPrefix=marc21

3. Römisch-Germanische Kommission:
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000007119&metadataPrefix=marc21
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000008119&metadataPrefix=marc21
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000009019&metadataPrefix=marc21
	* http://opac.dainst.org/OAI?verb=GetRecord&identifier=oai:dai-katalog:DAI14-000014419&metadataPrefix=marc21

You can see our mapping for this bibliographies. But in number 3) (Römisch-Germanische Kommission) you don't find information in field 552. 
In this case you find the descritors only in field 551, not in 552. other informations you can find in 553, 555, 557, 558.


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Aleph intern fields:	OAI-field:
--------------------	-------------------------------------------------------------------------------------------------------------------------------------------------

USE##			551## N = $a Deskriptor $9Sprachbezeichnung (ger, eng, fre, ita, spa, gre)

IT###			552## N  = $r subject/Schlagwort oder $m Schlagwort oder $e Schlagwort

CN###			553## N = $a Notation des Deskriptors

BT###			554## N =  $a Übergeordneter Deskriptor/broader term $1 Notation des übergeordneten Deskriptors $b Systemnummer des übergeordneten Deskriptors

SC###			555## N =  $a 	 $9 Sprachbezeichnung (ger, eng, fre, ita, spa, gre)

LV###			556## N =  $a Level (Inhalt 0)

RT###			557## N = $aVerwandter Deskriptor/related term $1 Notation des verwandten Datensatzes $b Systemnummer des verwandten Datensatzes

UF###			558## N  = $a Nicht-Deskriptor $9 Sprachbezeichnung (ger, eng, fre, ita, spa, gre)

SRT##			559## N = $a Sortierschlüssel (für die Deskriptoren des Thesaurus Rom nötig für die richtige Positionierung der Begriffe im Baum)  
			-> derzeit noch nicht in den Daten, da die Lieferung der spanischen Bibliographie dieses Feld nicht enthält.
			
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## My notes

* to get all the records from the OAI interface

	http://opac.dainst.org/OAI?verb=ListRecords&metadataPrefix=marc21&set=DAI_THS
	
* DAI_THS is the set containing all Zenon's Thesaurus data
* (mind the resumption_token thing)

## Mapping to STELLAR Console SKOS fields

concept_id <= 001
broader_id <= 554.1
related_id <= 557.1
definition <= 555.a
hidden_label <= 553.a


