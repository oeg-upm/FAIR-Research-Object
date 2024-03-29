from rocrate.rocrate import ROCrate
from rocrate_fairness.ro_fairness import ROCrateFAIRnessCalculator
from fuji_wrapper.fujiwrapper import FujiWrapper
<<<<<<<< HEAD:code/FAIROs.py
from somefFAIR.somefFAIR import SoftwareFAIRnessCalculator
========
from somef_wrapper.somefFAIR import SoftwareFAIRnessCalculator
>>>>>>>> dev-reliance:code/fair_assessment/full_ro_fairness.py
from foops_wrapper.foopswrapper import FoopsWrapper
import json
import validators
import visualizer
import argparse

class FAIROs:
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
            "tool-used": [tool_used],
        }
        if info:
            element["information"] = info
        element["checks"] = []
        return element

    def evaluate_ro(self):
        
        name = self.ro["title"]
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
        name = self.ro["title"]
        identifier = self.ro["identifier"]

        element = self.create_component_output(
            name, identifier, "ro-crate", "ro-crate-FAIR"
        )

        element["checks"] = ro_output["checks"]

        self.output["components"].append(element)

    def __add_ro_metadata_checks(self, element, element_id):
        #todo create urls for describing the terms of tools used
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
                    test["status"] = "ok"
        #extra_checks = self.ro_calculator.get_element_basic_checks(element_id)

        #for ec in extra_checks:
            #element["checks"].append(ec)

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

        """
        if aggregation_mode == 0:
            description = "The score is calculated by adding all the scores of the different components together. All passed tests and all total tests are added together and then the percentage is calculated"
            passed, total = 0, 0
            for component in self.output["components"]:
                for check in component["checks"]:
                    #passed += check["total_passed_tests"]
                    #total += check["total_tests_run"]
                    passed += 1
                    total += 1
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
        """
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
                if "sources" in check and all(key in check["sources"][0] for key in ('assessment', 'score','total_score')):
                    #score[cat]["tests_passed"] += 1 if check["sources"][0]["assessment"] == "pass" else 0
                    #score[cat]["total_tests"] += 1
                    if "score" in check and "total_score" in check:
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

        #if show_diagram:
        #    visualizer.generate_visual_graph(output_name)


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

FAIROs(args.ro_path).\
        calculate_fairness(args.evaluate_ro_metadata, 
                           args.aggregation_mode, 
                           args.output_file_name,
                           args.generate_diagram)


