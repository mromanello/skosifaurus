"""
To be executed in Jython. 
This script uses ST (String Template) v4. Since the Python port for v4 is not yet available, I had to use Jython (which turns out to be quite nice actually).
"""

import sys
sys.path.append('/Users/rromanello/Downloads/ST-4.0.7.jar')
import org.stringtemplate.v4 as st

options = {
	"base_uri" : "http://dainst.de/thesaurus#"
}

g = st.STGroupFile('/Users/rromanello/Documents/stellar/STELLAR.Templates/SKOS.stg')
conc = g.getInstanceOf('SKOS_CONCEPT')
conc.add('data',{"concept_id":"001"})
conc.add('options',options)
print conc.render()