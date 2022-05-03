from joblib import PrintTime
from rocrate.rocrate import ROCrate
from rocrate_fairness.ro_fairness import ROCrateFAIRnessCalculator
from fuji_wrapper.fujiwrapper import FujiWrapper, FujiWrapperv2
from someFAIR.somefFAIR import SoftwareFAIRnessCalculator
from foops_wrapper.foopswrapper import FoopsWrapper
import json
import validators


class ROFairnessCalculator():
    def __init__(self, ro_path) -> None:
        self.ro_path = ro_path

        self.rocrate = ROCrate(ro_path)
        self.ro          = self.rocrate.dereference("./").as_jsonld() # ro itself
        self.ro_parts    = [self.rocrate.dereference(part["@id"]).as_jsonld() for part in self.ro["hasPart"]] # all the parts of the ro
        self.ro_calculator = ROCrateFAIRnessCalculator(self.ro_path)        
        self.output = {"components":[]}
    
    def save_to_file(self):
            with open('ro-full-fairness.json', 'w') as f:
                json.dump(self.output, f, indent=4)
    
    def create_component_output(self, name, identifier, type, tool_used, info=""):
        element = { 
            "name":name,
            "identifier": identifier,
            "type":type, 
            "tool-used":tool_used,
        }
        if info:
            element["information"] = info
        element["checks"] = []
        return element
        
    
    def extract_ro(self):     
        ro_output = self.ro_calculator.calculate_fairness()
        name = ro_output["rocrate_path"]
        identifier = self.ro_calculator.get_identifier()
        
        element = self.create_component_output(name, identifier, "ro-crate", "ro-crate-FAIR")
        
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
        # self.output["components"].append(element)
        return element
    
    def __generate_partial_scores(self):
        for component in self.output["components"]:
            tmp = {"earned" : 0, "total" : 0 }
            score = {"Findable"    : dict(tmp),
                   "Accessible"    : dict(tmp),
                   "Interoperable" : dict(tmp),
                   "Reusable"      : dict(tmp)} 
            total_passed, total_tests = 0, 0
           
            for check in component["checks"]:
                cat = check["category_id"]
                score[cat]["earned"] += check["total_passed_tests"]
                score[cat]["total"]  += check["total_tests_run"]
            component["score"] = score

    def calculate_fairness(self, evaluate_ro_metadata=True):
        self.output["components"] = []
        software_valid_types = ["SoftwareSourceCode", "installUrl", "codeRepository"]
        self.extract_ro()
        
        for part in self.ro_parts:
            # TODO: a bit of refactor
            type = part["@type"]
            if type == "Dataset":
                if validators.url(part["@id"]):
                    fuji = FujiWrapperv2(part["@id"])
                    
                    component = self.__build_component( part["name"] if "name" in part else None,
                                                    fuji.get_identifier(), 
                                                    type, 
                                                    "F-uji",
                                                    fuji.get_checks())
                    
                    if evaluate_ro_metadata:
                        self.__add_ro_metadata_checks(component, part["@id"])
                    
                    self.output["components"].append(component)
                    
                else:
                    # Using the basic metadata analyzer
                    component = self.__build_component( part["name"] if "name" in part else None,
                                                    part["@id"],  
                                                    type, 
                                                    "F-uji",
                                                    "ro-crate-FAIR",
                                                    self.ro_calculator.get_element_basic_checks(part["@id"]),
                                                    "These checks have only been done by checking their metadata in the RO")
                    self.output["components"].append(component)
                    
            elif type == "SoftwareApplication":
                if any(vocab in part for vocab in software_valid_types):
                    
                    for vocab in software_valid_types:
                        if vocab in part:
                            repo_url_vocab = vocab
                            break
                    
                    sw = SoftwareFAIRnessCalculator(part[repo_url_vocab])
                    sw.calculate_fairness()
                    
                    component = self.__build_component( sw.get_name(),
                                                    sw.get_identifier(), 
                                                    type, 
                                                    "somef-fairness",
                                                    sw.get_checks(),
                                                    "These checks have only been done by checking their metadata in the RO")
                    
                    if evaluate_ro_metadata:
                        self.__add_ro_metadata_checks(component, part["@id"])
                    
                    self.output["components"].append(component)              
                    
                else:
                    # Using the basic metadata analyzer
                    component = self.__build_component( part["name"]       if "name"       in part else None,
                                                    part["identifier"] if "identifier" in part else None, 
                                                    type, 
                                                    "ro-crate-FAIR",
                                                    self.ro_calculator.get_element_basic_checks(part["@id"]),
                                                    "These checks have only been done by checking their metadata in the RO")
                    self.output["components"].append(component)
                    
            elif type == "Ontology":
                onto_uri = part["@id"]
                onto = FoopsWrapper(onto_uri)
                
                component = self.__build_component( onto.get_ontology_title(),
                                                        onto.get_ontology_URI(), 
                                                        type, 
                                                        "foops",
                                                        onto.get_ontology_checks())
                
                if evaluate_ro_metadata:
                    self.__add_ro_metadata_checks(component, part["@id"])
                
                self.output["components"].append(component)
                
            else:
                
                if validators.url(part["@id"]):
                    fuji = FujiWrapperv2(part["@id"])
                    
                    component = self.__build_component(part["name"] if "name" in part else None,
                                                   fuji.get_identifier(), 
                                                   type, 
                                                   fuji.get_checks(),
                                                   "F-uji")
                    if evaluate_ro_metadata:
                        self.__add_ro_metadata_checks(component, part["@id"])
                    
                    self.output["components"].append(component)
                    
                else:
                    # Using the basic metadata analyzer
                    component = self.__build_component( part["name"]       if "name"       in part else None,
                                                    part["identifier"] if "identifier" in part else None, 
                                                    type, 
                                                    "ro-crate-FAIR",
                                                    self.ro_calculator.get_element_basic_checks(part["@id"]),
                                                    "These checks have only been done by checking their metadata in the RO")
                    self.output["components"].append(component)
        
        self.__generate_partial_scores()
                
ro_fairness = ROFairnessCalculator("ro-example-2/")

ro_fairness.calculate_fairness(evaluate_ro_metadata=True)
ro_fairness.save_to_file()
