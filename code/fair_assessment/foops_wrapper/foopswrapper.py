import os
from subprocess import Popen
import  json

class FoopsWrapper:
    def __init__(self, onto_uri) -> None:
        self.onto_uri = onto_uri
        cmd = f'curl -X POST "https://foops.linkeddata.es/assessOntology" -H "accept: application/json;charset=UTF-8" -H "Content-Type: application/json;charset=UTF-8" -d "{{ \\"ontologyUri\\": \\"{ self.onto_uri}\\"}}"'
        result = os.popen(cmd).read()

        self.raw_output = json.loads(result)
    
    def get_ontology_URI(self):
        return self.raw_output["ontology_URI"]
    
    def get_ontology_title(self):    
        return self.raw_output["ontology_title"]
    
    def get_ontology_checks(self):
        checks = self.raw_output["checks"]
        
        for check in checks:
            del check["id"] 
        
        return checks
    