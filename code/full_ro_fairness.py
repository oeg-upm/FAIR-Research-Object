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
            "tool-used": tool_used,
        }
        if info:
            element["information"] = info
        element["checks"] = []
        return element

    def extract_ro(self):
        ro_output = self.ro_calculator.calculate_fairness()
        name = ro_output["rocrate_path"]
        identifier = self.ro_calculator.get_identifier()

        element = self.create_component_output(
            name, identifier, "ro-crate", "ro-crate-FAIR"
        )

        element["checks"] = ro_output["checks"]

        self.output["components"].append(element)

    def __add_ro_metadata_checks(self, element, element_id):
        element["tool-used"] += " + ro-metadata"
        extra_checks = self.ro_calculator.get_element_basic_checks(element_id)

        for ec in extra_checks:
            element["checks"].append(ec)

    def __build_component(self, name, identifier, type, tool_used, checks, info=""):
        element = self.create_component_output(name, identifier, type, tool_used, info)
        element["checks"] = checks
        return element

    def __generate_overall_score(self, aggregation_mode):
        overall_score = {
            "description" : "",
            "score" : 0
        }
        
        if aggregation_mode == 0:
            description = "The score is calculated by adding all the scores of the different components together. All passed tests and all total tests are added together and then the percentage is calculated"
            passed, total = 0, 0
            for component in self.output["components"]:
                for check in component["checks"]:
                    passed += check["total_passed_tests"]
                    total += check["total_tests_run"]
            overall_score["score"] = round((passed / total)*100, 2)
            overall_score["total_sum"] = {"total_passed_tests" : passed, "total_run_tests": total}
                
        elif aggregation_mode == 1:
            description = "The score is calculated by averaging the scores of its components. The component score is the average of the score of each FAIR principle"
            component_scores = []
            for component in self.output["components"]:
                principles_scores = []
                for score_category in component["score"]:
                    score_category = component["score"][score_category]
                    if score_category["total_tests"] == 0: continue 
                    principles_scores.append(round((score_category["tests_passed"] / score_category["total_tests"]) * 100 , 2))
                component_scores.append(round(sum(principles_scores)/len(principles_scores),2))
            overall_score["score"] = round(sum(component_scores)/len(component_scores),2)
        
        overall_score["description"] = description    
        self.output["overall_score"] = overall_score    
        
    def __generate_partial_scores(self):
        for component in self.output["components"]:
            tmp = {"tests_passed": 0, "total_tests": 0}
            score = {
                "Findable": dict(tmp),
                "Accessible": dict(tmp),
                "Interoperable": dict(tmp),
                "Reusable": dict(tmp),
            }

            for check in component["checks"]:
                cat = check["category_id"]
                score[cat]["tests_passed"] += check["total_passed_tests"]
                score[cat]["total_tests"] += check["total_tests_run"]
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

            if evaluate_ro_metadata:
                self.__add_ro_metadata_checks(component, element["@id"])

            self.output["components"].append(component)

        else:
            # Using the basic metadata analyzer
            component = self.__build_component(
                element["name"] if "name" in element else None,
                element["@id"],
                element["@type"],
                "F-uji",
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
                fuji.get_checks(),
                "F-uji",
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
        
        self.extract_ro()

        for element in self.ro_parts:

            type = element["@type"]
            
            if type == "Dataset":   
               self.__evaluate_dataset(element, evaluate_ro_metadata)
                
            elif type == "SoftwareApplication":
               self.__evaluate_software_application(element, evaluate_ro_metadata)

            elif type == "Ontology":
                self.__evaluate_ontology(element, evaluate_ro_metadata)
                
            else:
                self.__evaluate_other(element, evaluate_ro_metadata)
            

        self.__generate_partial_scores()
        self.__generate_overall_score(aggregation_mode)


    def calculate_fairness(self, evaluate_ro_metadata, aggregation_mode, output_name ,show_diagram):
        
        self.__calculate_fairness(evaluate_ro_metadata, aggregation_mode)
        self.save_to_file(output_name)

        if show_diagram:
            visualizer.generate_visual_graph(output_name)


def parse_boolean(value):
    value = value.lower()

    if value in ["true", "yes", "y", "1", "t"]:
        return True
    elif value in ["false", "no", "n", "0", "f"]:
        return False

    return False

parser = argparse.ArgumentParser(description='Tool to calculate the FAIRness of a Reserch Objects.')

parser.add_argument('-ro', dest='ro_path', type=str, required=True, 
                    help='The location where the Reserch Object is. Do not include the "ro-crate-metadata.json"')

parser.add_argument('-o', dest='output_file_name', type=str, default="ro-fairness.json" ,required=False, 
                    help='Output file name including ".json"')

parser.add_argument('-m', dest='evaluate_ro_metadata', type=parse_boolean, default=False ,required=False, 
                    help='Whether or not the metadata of the components of the Reserch Object are analyzed')

parser.add_argument('-a', dest='aggregation_mode', type=int, default=0 ,required=False, 
                    help='Select the different aggregation mode'
                    '\n1: The score is calculated by adding all the scores of the different components together.'
                          'All passed tests and all total tests are added together and then the percentage is calculated'
                    '\n2: The score is calculated by averaging the scores of its components.'
                          'The component score is the average of the score of each FAIR principle')

parser.add_argument('-d', dest='generate_diagram', type=bool, default=False ,required=False, 
                    help='Generate a visual representation')

args = parser.parse_args()

ROFairnessCalculator(args.ro_path).\
        calculate_fairness(args.evaluate_ro_metadata, 
                           args.aggregation_mode, 
                           args.output_file_name,
                           args.generate_diagram)


