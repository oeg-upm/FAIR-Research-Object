from rocrate.rocrate import ROCrate
import json
import requests

from os import listdir
from os.path import isfile, isdir, join
import validators

def extract_all_values_recursively(element, values):
    if type(element) is str:
        values.append(element)
    elif type(element) is dict:
        for key in element:
            extract_all_values_recursively(element[key], values)
    elif type(element) is list:
        for ele in element:
            extract_all_values_recursively(ele, values)


class ROCrateFAIRnessCalculator():
    def __init__(self, ro_path) -> None:
        self.ro_path = ro_path

        with open(self.ro_path + "/ro-crate-metadata.json", "r") as f:
            self.ro_raw_plain =  ' '.join(f.read().split())

        with open(self.ro_path + "/ro-crate-metadata.json", "r") as f:
            self.ro_json = json.load(f)

        self.ro = ROCrate("example-ro-crate") # TODO

        self.fair_output = {"checks": []}

    def calculate_fairness(self):
        self.evaluate_f1()
        self.evaluate_f2()
        self.evaluate_f3()
        self.evaluate_i2()
        self.evaluate_r1_1()
        self.evaluate_r1_2()
        print(self.fair_output)

    def save_to_file(self):
        with open('ro-crate-fairness.json', 'w') as f:
            json.dump(self.fair_output, f, sort_keys=True, indent=4)

    def evaluate_f1(self):
        check = {"principle_id": "F1",
                 "category_id" : "Findable",
                 "title"       : "(Meta)data are assigned a persistent identifier",
                 "description" : "This check verifies if the RO has a persintance identifier (w3id, doi, purl or w3).",
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
                        check["explanation"] = f"The identifier is persistent [{identifier}]"
                    else:
                        check["status"] = "error"
                        check["explanation"] = f"The identifier [{identifier}] does not exist"
                else:
                    check["status"] = "error"
                    check["explanation"] = f"The identifier ({identifier}) of the root data entity is not persistent. The identifier should be store in any of this [w3id.org, doi.org, purl.org, www.w3.org]"
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

    def evaluate_i2(self):
        check = {"principle_id": "I2",
                 "category_id" : "Interoperable",
                 "title"       : "(Meta)data use vocabularies that follow FAIR principles",
                 "description" : "This check verifies if the RO use a FAIR context (schema.org)",
                 "total_passed_tests": 0,
                 "total_tests_run"   : 0
                 }

        # test 1
        keys = []
        extract_all_values_recursively(self.ro_json["@context"], keys)
        valid_vocab = ["schema.org"]

        invalid_vocab, notknown_vocab = [], []

        for key in keys:
            # check if the URI of the context belong to a known profiles (schema and w3id)
            if any(context in key for context in valid_vocab):
                # check if the URI is available
                response = requests.get(key)
                if response.status_code >= 400:
                    invalid_vocab.append(key)
            else:
                notknown_vocab.append(key)
        check["total_tests_run"] += 2 # one for the known profiles and other for being accessible
        check["explanation"] = []

        if len(notknown_vocab) == 0:
            check["total_passed_tests"] += 1
            check["explanation"].append( f"All the vocabularies are FAIR")
        else:
            check["status"] = "error"
            check["explanation"].append( f"These vocabularies do not belong to {', '.join(valid_vocab)}: {', '.join(notknown_vocab)}")

        if len(invalid_vocab) == 0:
            check["total_passed_tests"] += 1
            check["explanation"].append("All the URIs are accessibles")
        else:
            check["status"] = "error"
            check["explanation"].append( f"These URIs are not accessibles: {', '.join(invalid_vocab)}")

        if not "status" in check:
            check["status"] = "ok"

        self.fair_output["checks"].append(check)

    def evaluate_r1_1(self):
        check = {"principle_id": "R1.1",
                "category_id" : "Reusable",
                "title"       : "(Meta)data are released with a clear and accessible data usage license",
                "description" : "This check verifies whether the RO has a licence. It also checks that there is a licence in the entity data of [CreativeWork, Dataset, File]",
                "total_passed_tests": 0,
                "total_tests_run"   : 0
                }
        check["explanation"] = []

        # test 1. Licence in root data entity
        try:
            root_data_entity = self.ro.metadata.as_jsonld()

            if "license" in root_data_entity:
                check["status"] = "ok"
                check["explanation"].append("The root data entity has a license")
                check["total_passed_tests"] += 1
            else:
                check["status"] = "error"
                check["explanation"].append("The root data entity has not a license")

        except:
            check["status"] = "error"
            check["explanation"].append("No root data entity. Cound not check the license of the RO")
        check["total_tests_run"] += 1


        # test 2. License in data entities
        all_elements = self.ro_json["@graph"]
        valid_types = ["CreativeWork", "Dataset", "File"]

        def check_nested_license(element):
            ''' This function accepts a nested dictionary as argument
                and iterate over all values of nested dictionaries.
                It returns True if it finds a key named "license".
            '''
            if "license" in element:
                return True

            for _ , value in element.items():
                if isinstance(value, dict):
                    if "license" in value:
                        return True
                    else:
                        check_nested_license(value)

        unlicensed_elements = [element["@id"] for element in all_elements if any(type in element["@type"] for type in valid_types) and not check_nested_license(element)]

        if len(unlicensed_elements) == 0:
            check["total_passed_tests"] += 1
            check["explanation"].append(f"All the data entities of type {valid_types} have a license")
        else:
            check["explanation"].append(f"These entities of type {valid_types} have not a license: {' ,'.join(unlicensed_elements)}")
        check["total_tests_run"] += 1

        self.fair_output["checks"].append(check)

    def evaluate_r1_2(self):
        check = {"principle_id": "R1.2",
                 "category_id": "Reusable",
                 "title": "(Meta)data are associated with detailed provenance",
                 "description": "This check verifies that: "
                    "Dataset entities has an author, datePublished and citation. "
                    "Files has an author",
                 "total_passed_tests": 0,
                 "total_tests_run": 0,
                 "explanation" : []
                 }
        
        # test 1
        all_elements = self.ro_json["@graph"]
        
        # remove the root entity data
        for i, element in enumerate(all_elements):
            if element["@id"] == self.ro.metadata.as_jsonld()["@id"]:
                all_elements.pop(i)
                break
        
        internal_checks = [
            ["Dataset", ["author", "datePublished", "citation"]],
            ["File", ["author"]]
        ]

        for type_check in internal_checks:
            for element in all_elements:
                if element["@type"] == type_check[0]:
                    tmp_missing_data = []
                    for key in type_check[1]:
                        if not key in element:
                            tmp_missing_data.append(key)
                    if len(tmp_missing_data) > 0:
                        check["explanation"].append(f"The {element['@type']} with @id={element['@id']} do not have [{', '.join(tmp_missing_data)}]")        
       
        check["total_tests_run"] += 1

        if len(check["explanation"]) == 0:
            check["total_passed_tests"] += 1
            for type_check in internal_checks:
                 check["explanation"].append(f"All the {type_check[0]} has {', '.join(type_check[1])}")

        self.fair_output["checks"].append(check)


roFAIR = ROCrateFAIRnessCalculator("example-ro-crate")
roFAIR.calculate_fairness()
roFAIR.save_to_file()





