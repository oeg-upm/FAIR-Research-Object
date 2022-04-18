import os
from subprocess import Popen
import  json

class FoopsWrapper:

    def get_metric(self, url):
        cmd = f'curl -X POST "https://foops.linkeddata.es/assessOntology" -H "accept: application/json;charset=UTF-8" -H "Content-Type: application/json;charset=UTF-8" -d "{{ \\"ontologyUri\\": \\"{url}\\"}}"'
        result = os.popen(cmd).read()

        json_object = json.loads(result)
        return json_object