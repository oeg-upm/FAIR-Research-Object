from rocrate.rocrate import ROCrate
from rocrate_fairness.ro_fairness import ROCrateFAIRnessCalculator
# from fuji_wrapper.fujiwrapper import FujiWrapper
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
        self.output = {}
    
    def save_to_file(self):
            with open('ro-full-fairness.json', 'w') as f:
                json.dump(self.output, f, sort_keys=True, indent=4)
            
    def extract_ro(self):
        ro_calculator = ROCrateFAIRnessCalculator(self.ro_path)        
        ro_output = ro_calculator.calculate_fairness()
        
        # this is the common header. TODO: extract to function
        ro_element = { 
            "name":ro_output["rocrate_path"],
            "identifier": ro_calculator.get_identifier(),
            "type":"ro-crate", 
            "tool-used":"ro-crate-FAIR"}
        ro_element["checks"] = ro_output["checks"]
        self.output["components"] = [ro_element]
    
        
    def calculate_fairness(self):
        self.output["components"] = []
    
        self.extract_ro()
        
        for part in self.ro_parts:
            type = part["@type"]
            if type == "Dataset":
                break
                uri = part["identifier"] # identifier?? @id???
                fuji = FujiWrapper()
                fuji_results = fuji.get_metric(uri)
                print("F-UJI results:", fuji_results)
            
            elif type == "SoftwareApplication":
                repo_url = part["installUrl"] # only this?
                sw = SoftwareFAIRnessCalculator(repo_url)
                print("SOMEEEEEEEEEEEEF ",sw.calculate_fairness())
                # TODO
                
            elif type == "Ontology":
                onto_uri = part["@id"] # id?? , identifier?
                onto = FoopsWrapper(onto_uri)
                onto.get_metric()
                print("FOPPPPPPPPPPPPS ", onto.get_metric() )
                
            else:
                # fuji o ro
                if validators.url(part["@id"]): # id? identifier?
                    # fuji = FujiWrapper()
                    # fuji_results = fuji.get_metric(part["@id"])
                    pass
                else:
                # evaluate fairness checking author, license, identifier, description...
                    pass
                
ro_fairness = ROFairnessCalculator("ro-example-2/")
ro_fairness.extract_ro()
ro_fairness.save_to_file()
ro_fairness.calculate_fairness()
