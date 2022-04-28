import os
from subprocess import Popen
import  json

class FoopsWrapper:
    def __init__(self, onto_uri) -> None:
        self.onto_uri = onto_uri

    def get_metric(self):
        cmd = f'curl -X POST "https://foops.linkeddata.es/assessOntology" -H "accept: application/json;charset=UTF-8" -H "Content-Type: application/json;charset=UTF-8" -d "{{ \\"ontologyUri\\": \\"{ self.onto_uri}\\"}}"'
        result = os.popen(cmd).read()

        json_object = json.loads(result)
        return json_object