from rocrate.rocrate import ROCrate
import json
import requests

class ROCrateFAIRnessCalculator():
    def __init__(self, ro_path) -> None:
        self.ro_path = ro_path
        
        with open(self.ro_path) as f:
            self.ro_raw = json.load(f)
        
        self.ro = ROCrate("example-ro-crate") # TODO

        self.fair_output = {}
        self.fair_output["checks"] = []
    
    def calculate_fairness(self):
        # self.evaluate_f1()
        self.evaluate_f2()
        print(self.fair_output)

    def evaluate_f1(self):
        check = {"principle_id": "F1",
                 "category_id" : "Findable",
                 "title"       : "(Meta)data are assigned a globally unique and persistent identifier",
                 "description" : "This check verifies if the RO has a persintance and unique identifier (w3id, doi, purl or w3).",
                 "total_passed_tests": 0,
                 "total_tests_run"   : 0
                 }

        # test 1
        try:
            root_data_entity = self.ro.metadata.as_jsonld()
            if "identifier" in root_data_entity:
                identifier = root_data_entity["identifier"]
                valid_domains = ["w3id.org", "doi.org", "purl.org", "www.w3.org"]

                if any(domain in identifier for domain in valid_domains):
                    response = requests.get(identifier)
                    if response.status_code < 400:
                        check["status"] = "ok"
                        check["total_passed_tests"] += 1
                        check["explanation"] = "The identifier is unique and persistent"
                    else:
                        check["status"] = "error"
                        check["explanation"] = "The identifier does not exist"
                else:
                    check["status"] = "error"
                    check["explanation"] = "Not using a persistent id. We checked w3id, purl, DOI and W3C"
            else:
                check["status"] = "error"
                check["explanation"] = "No identifier in root data entity"
            check["total_tests_run"] += 1
        except:
            check["status"] = "error"
            check["explanation"] = "No root data entity"

        self.fair_output["checks"].append(check)

    def evaluate_f2(self):
        check = {"principle_id": "F2",
                "category_id" : "Findable",
                "title"       : "Data are described with rich metadata ",
                "description" : "This check verifies if the the following minimum metadata [author, license, description and at least one resource] are present in the ro-crate",
                "total_passed_tests": 0,
                "total_tests_run"   : 0
                }
        
        missing_metadata_error = "Missing the following metadata: "
        missing_metadata = []
        

        try:
            root_data_entity = self.ro.metadata.as_jsonld()
        except:
            check["status"] = "error"
            check["explanation"] = "No root data entity"
            check["total_tests_run"] += 1 # 1 or 4 ???

        # test 1. Autor
        min_meta = ["author", "license", "description"]
        for meta in min_meta:
            if not meta in root_data_entity:
                missing_metadata.append(meta)
        
        if not len(self.ro_raw["@graph"] ) > 1:
            missing_metadata.append("at least one resource")

                
        if len(missing_metadata) > 0:
            check["status"] = "error"
            missing_metadata_error += ", ".join(missing_metadata)
            check["explanation"] = missing_metadata_error
        else:
            check["status"] = "ok"
            check["total_passed_tests"] += 1
            check["explanation"] = "The ro-crate contains the following metadata [author, license, description and at least one resource]"
        check["total_tests_run"] += 1        

        self.fair_output["checks"].append(check)


roFAIR = ROCrateFAIRnessCalculator("../../test_examples/ro-crate.json")
roFAIR.calculate_fairness()




