from rocrate.rocrate import ROCrate
import json
import requests

from os import listdir
from os.path import isfile, isdir, join
import validators

class ROCrateFAIRnessCalculator():
    def __init__(self, ro_path) -> None:
        self.ro_path = ro_path
        
        with open(self.ro_path + "/ro-crate-metadata.json", "r") as f:
            self.ro_raw_plain =  ' '.join(f.read().split())
        
        with open(self.ro_path + "/ro-crate-metadata.json", "r") as f:
            self.ro_json = json.load(f)

        self.ro = ROCrate("example-ro-crate") # TODO

        self.fair_output = {}
        self.fair_output["checks"] = []
    
    def calculate_fairness(self):
        self.evaluate_f1()
        self.evaluate_f2()
        self.evaluate_f3()
        print(self.fair_output)
    
    def save_to_file(self):
        with open('ro-crate-fairness.json', 'w') as f:
            json.dump(self.fair_output, f, sort_keys=True, indent=4)

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
                        check["explanation"] = f"The identifier is unique and persistent [{identifier}]"
                    else:
                        check["status"] = "error"
                        check["explanation"] = f"The identifier [{identifier}] does not exist"
                else:
                    check["status"] = "error"
                    check["explanation"] = f"The identifier ({identifier}) of the root data entity is not unique and persistent. The identifier should be store in any of this [w3id.org, doi.org, purl.org, www.w3.org]"
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
                "title"       : "Data are described with rich metadata",
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
            check["total_tests_run"] += 1 

        # test 1
        min_meta = ["author", "license", "description"]
        for meta in min_meta:
            if not meta in root_data_entity:
                missing_metadata.append(meta)
        
        if not len(self.ro_json["@graph"] ) > 1:
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

    def evaluate_f3(self):
        check = {"principle_id": "F3",
                "category_id" : "Findable",
                "title"       : "Metadata clearly and explicitly include the identifier of the data they describe",
                "description" : "This check verifies that the elements described in the ro exist in the directory given (or in their URIs)",
                "total_passed_tests": 0,
                "total_tests_run"   : 0
                }
        
        # test 1
        all_elements = self.ro_json["@graph"]
        files_in_dir = [f for f in listdir(self.ro_path) if isfile(join(self.ro_path, f))]

        errors_found = []
        
        for element in all_elements:
            id = element["@id"]
            
            if id in files_in_dir:
                # print("FILE FOUND: ", id)
                pass

            elif validators.url(id):
                try:
                    response = requests.get(id)
                except:
                    # print("BAD IRI: ", id)
                    errors_found.append(f"This IRI has not been found: {id}")
                    
                if response.status_code < 400:
                    # print("IRI FOUND: ", id)
                    pass
                else:
                    # print("IRI NOT FOUND: ", id)
                    errors_found.append(f"This IRI has not been found: {id}")
                    
            else:
                path = join(self.ro_path, id)
                if isdir(path):
                    # print("DIR FOUND: ", id)
                    pass
                elif isfile(path):
                    # print("FILE FOUND: ", id)
                    pass
                else:
                    # check if the id was already created:
                    if self.ro_raw_plain.count(f'"@id": "{id}"') > 1:
                        # print("ALREADY CREATED ID: ", id)
                        pass
                    else:
                        errors_found.append(f"Unknown id: {id}")
                        print("ID NOT CREATED: ", id)

        if len(errors_found) > 0:
            check["status"] = "error"
            check["explanation"] = errors_found
        else:
            check["status"] = "ok"
            check["explanation"] = "All element identifiers exist"
            check["total_passed_tests"] += 1

        check["total_tests_run"] += 1
        self.fair_output["checks"].append(check)

            

roFAIR = ROCrateFAIRnessCalculator("example-ro-crate")
roFAIR.calculate_fairness()
roFAIR.save_to_file()




