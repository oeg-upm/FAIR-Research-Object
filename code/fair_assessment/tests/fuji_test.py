import unittest
import requests

class TestFUJI(unittest.TestCase):
     def test_type(self):
        url = ""
        token = ""
        json_object={"metadata_service_endpoint": "http://ws.pangaea.de/oai/provider","metadata_service_type": "oai_pmh","object_identifier":"https://w3id.org/ro-id-dev/63617473-80c0-4057-9a43-57512721b054/resources/ca96b58a-3553-4cfc-a401-109bf91e74cc","test_debug": true,"use_datacite": true}
        headers = {"Content-Type":"application/json","Authorization":token}
        r = requests.post(url, json=json_object) 
        print(r)

if __name__ == '__main__':
    unittest.main()