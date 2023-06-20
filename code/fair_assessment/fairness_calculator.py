from rocrate.rocrate import ROCrate
from rocrate_fairness.ro_fairness import ROCrateFAIRnessCalculator
from fuji_wrapper.fujiwrapper import FujiWrapper
from someFAIR.somefFAIR import SoftwareFAIRnessCalculator
from foops_wrapper.foopswrapper import FoopsWrapper
import json
import validators
import visualizer
import argparse

class ROFairnessCalculator:
    def __init__(self, ro_path) -> None:
        self.ro_path = ro_path

        self.rocrate = ROCrate(ro_path)
        self.ro = self.rocrate.dereference("./").as_jsonld()  # ro itself
        self.ro_parts = [
            self.rocrate.dereference(part["@id"]).as_jsonld()
            for part in self.ro["hasPart"]
        ]  # all the parts of the ro
        self.ro_calculator = ROCrateFAIRnessCalculator(self.ro_path)
        self.output = {"components": []}

    def save_to_file(self, filename="ro-full-fairness.json"):
        with open(filename, "w") as f:
            json.dump(self.output, f, indent=4)
        

    def create_component_output(self, name, identifier, type, tool_used, info=""):
        element = {
            "name": name,
            "identifier": identifier,
            "type": type,
            "tool-used":[tool_used],
        }
        if info:
            element["information"] = info
        element["checks"] = []
        return element

    def evaluate_ro(self):
        
        name = self.ro["name"]
        identifier = self.ro["identifier"]
        identifier_rocrate = self.ro["@id"]

        element = self.create_component_output(
            name, identifier, "ro-crate", "ro-crate-FAIR"
        )

        if validators.url(identifier):
            fuji = FujiWrapper(identifier)

            component = self.__build_component(
                element["name"] if "name" in element else None,
                fuji.get_identifier(),
                "ro-crate",
                "F-uji",
                fuji.get_checks(),
            )
 
        self.__add_ro_metadata_checks(component, identifier_rocrate)


        self.output["components"].append(component)

    def extract_ro(self):
        ro_output = self.ro_calculator.calculate_fairness()
        name = self.ro["name"]
        identifier = self.ro["identifier"]

        element = self.create_component_output(
            name, identifier, "ro-crate", "ro-crate-FAIR"
        )

        element["checks"] = ro_output["checks"]

        self.output["components"].append(element)

    def __add_ro_metadata_checks(self, element, element_id):
        print("TOOL:"+str(element["tool-used"]))
        element["tool-used"].append("ro-crate-metadata") 
        for test in element["checks"]:
            if test["status"]=="fail":
                fuji_score = test["sources"][0]["score"]
                extra_checks = self.ro_calculator.rocrate_principle_check(element_id,test["principle_id"])
                test["sources"].append(extra_checks)
                if "score" in extra_checks:
                    if fuji_score > extra_checks["score"]:
                        test["score"] = fuji_score
                    else:
                        test["score"] = extra_checks["score"]
                    test["total_score"] = extra_checks["total_score"]
                if "assessment" in extra_checks and extra_checks["assessment"] == "pass":
                    test["status"] = "pass"
            else:
                test["score"] = test["sources"][0]["score"]
                test["total_score"] = test["sources"][0]["total_score"]

    def __build_component(self, name, identifier, type, tool_used, checks, info=""):
        element = self.create_component_output(name, identifier, type, tool_used, info)
        element["checks"] = checks
        return element

    def __generate_overall_score(self, aggregation_mode):
        overall_score = {
            "description" : "",
            "score" : 0
        }
        
        score = 0.0
        total_score = 0.0

        for component in self.output["components"]:
            for check in component["checks"]:
                if "score" in check and "total_score" in check:
                    score += check["score"]
                    total_score += check["total_score"]

        overall_score["score"] = round((score / total_score) * 100,2)

        overall_score["description"] = "Formula: score of each principle / total score"    
        self.output["overall_score"] = overall_score    
        
    def __generate_partial_scores(self):
        for component in self.output["components"]:
            tmp = {"tests_passed": 0, "total_tests": 0, "score": 0, "total_score":0}
            score = {
                "Findable": dict(tmp),
                "Accessible": dict(tmp),
                "Interoperable": dict(tmp),
                "Reusable": dict(tmp),
            }

            for check in component["checks"]:
                cat = check["category_id"]
                if "status" in check:
                    if check['status'] == "pass":
                        score[cat]["tests_passed"] = score[cat]["tests_passed"] +1
                    score[cat]["total_tests"] = score[cat]["total_tests"] + 1
                if "score" in check:
                    score[cat]["score"] += check["score"]
                    score[cat]["total_score"] += check["total_score"]

            component["score"] = score

    def __evaluate_dataset(self, element, evaluate_ro_metadata):
        if validators.url(element["@id"]):
            fuji = FujiWrapper(element["@id"])

            component = self.__build_component(
                element["name"] if "name" in element else None,
                fuji.get_identifier(),
                element["@type"],
                "F-uji",
                fuji.get_checks(),
            )

            
            self.__add_ro_metadata_checks(component, element["@id"])

            self.output["components"].append(component)

        else:
            # Using the basic metadata analyzer
            component = self.__build_component(
                element["name"] if "name" in element else None,
                element["@id"],
                element["@type"],
                "ro-crate-FAIR",
                self.ro_calculator.get_element_basic_checks(element["@id"]),
                "These checks have only been done by checking their metadata in the RO",
            )
            self.output["components"].append(component)

    def __evaluate_software_application(self, element, evaluate_ro_metadata):
        software_valid_types = ["SoftwareSourceCode", "installUrl", "codeRepository"]
        if any(vocab in element for vocab in software_valid_types):
    
            for vocab in software_valid_types:
                if vocab in element:
                    repo_url_vocab = vocab
                    break

            sw = SoftwareFAIRnessCalculator(element[repo_url_vocab])
            sw.calculate_fairness()

            component = self.__build_component(
                sw.get_name(),
                sw.get_identifier(),
                element["@type"],
                "somef-fairness",
                sw.get_checks(),
                "These checks have only been done by checking their metadata in the RO",
            )

            if evaluate_ro_metadata:
                self.__add_ro_metadata_checks(component, element["@id"])

            self.output["components"].append(component)

        else:
            # Using the basic metadata analyzer
            component = self.__build_component(
                element["name"] if "name" in element else None,
                element["identifier"] if "identifier" in element else None,
                element["@type"],
                "ro-crate-FAIR",
                self.ro_calculator.get_element_basic_checks(element["@id"]),
                "These checks have only been done by checking their metadata in the RO",
            )
            self.output["components"].append(component)
    
    def __evaluate_ontology(self, element, evaluate_ro_metadata ):
        onto_uri = element["@id"]
        onto = FoopsWrapper(onto_uri)

        component = self.__build_component(
            onto.get_ontology_title(),
            onto.get_ontology_URI(),
            element["@type"],
            "foops",
            onto.get_ontology_checks(),
        )

        if evaluate_ro_metadata:
            self.__add_ro_metadata_checks(component, element["@id"])

        self.output["components"].append(component)
    
    def __evaluate_other(self, element, evaluate_ro_metadata):
        if validators.url(element["@id"]):
            fuji = FujiWrapper(element["@id"])

            component = self.__build_component(
                element["name"] if "name" in element else None,
                fuji.get_identifier(),
                element["@type"],
                "F-uji",
                fuji.get_checks(),     
            )
            if evaluate_ro_metadata:
                self.__add_ro_metadata_checks(component, element["@id"])

            self.output["components"].append(component)

        else:
            # Using the basic metadata analyzer
            component = self.__build_component(
                element["name"] if "name" in element else None,
                element["identifier"] if "identifier" in element else None,
                element["@type"],
                "ro-crate-FAIR",
                self.ro_calculator.get_element_basic_checks(element["@id"]),
                "These checks have only been done by checking their metadata in the RO",
            )
            self.output["components"].append(component)
            
            
    def __calculate_fairness(self, evaluate_ro_metadata, aggregation_mode):
        self.output["components"] = []
        
        self.evaluate_ro()

        for element in self.ro_parts:

            type = element["@type"]   
            if "Dataset" in type and not "http://purl.org/wf4ever/wf4ever#Folder" in type: 
               self.__evaluate_dataset(element, evaluate_ro_metadata)

            elif type == "SoftwareApplication":
               self.__evaluate_software_application(element, evaluate_ro_metadata)

            elif type == "Ontology":
                self.__evaluate_ontology(element, evaluate_ro_metadata)
            elif "File" in type:
                self.__evaluate_dataset(element, evaluate_ro_metadata)
            

        self.__generate_partial_scores()
        self.__generate_overall_score(aggregation_mode)


    def calculate_fairness(self, evaluate_ro_metadata, aggregation_mode, output_name ,show_diagram):
        
        self.__calculate_fairness(evaluate_ro_metadata, aggregation_mode)
        self.save_to_file(output_name)


def parse_boolean(value):
    value = value.lower()

    if value in ["true", "yes", "y", "1", "t"]:
        return True
    elif value in ["false", "no", "n", "0", "f"]:
        return False

    return False
