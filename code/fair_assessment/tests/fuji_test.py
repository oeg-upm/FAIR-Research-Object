import unittest
import requests

class TestFUJI(unittest.TestCase):
     def test_type(self):
        url = ""
        token = ""
        json_object={"metadata_service_endpoint": "http://ws.pangaea.de/oai/provider","metadata_service_type": "oai_pmh","object_identifier":"https://w3id.org/ro-id-dev/63617473-80c0-4057-9a43-57512721b054/resources/ca96b58a-3553-4cfc-a401-109bf91e74cc","test_debug": True,"use_datacite": True}
        headers = {"Content-Type":"application/json","Authorization":token}
        r = requests.post(url, headers = headers, json=json_object) 
        result_json = r.json()

        self.assertEqual(result_json["results"][0]["id"],1)
        self.assertEqual(result_json["results"][0]["metric_identifier"],"FsF-F1-01D")
        self.assertEqual(result_json["results"][0]["metric_tests"]["FsF-F1-01D-1"]["metric_test_score"],1)
        self.assertEqual(result_json["results"][0]["metric_tests"]["FsF-F1-01D-1"]["metric_test_status"],"pass")
        self.assertEqual(result_json["results"][0]["metric_tests"]["FsF-F1-01D-1"]["metric_test_score"],0)
        self.assertEqual(result_json["results"][0]["metric_tests"]["FsF-F1-01D-1"]["metric_test_status"],"fail")


if __name__ == '__main__':
    unittest.main()