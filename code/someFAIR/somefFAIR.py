import os
import json

class SoftwareFAIRnessCalculator:
    def __init__(self, repo_url):
        self.repoURL = repo_url
        self.tmp_file = self.generate_temp_file_name()

        # store the somef output and reuse it if needed
        if not os.path.exists(self.tmp_file):
            os.system(f"somef describe -r {self.repoURL} -o {self.generate_temp_file_name()} -t 0.8")            
            # self.read_temp_file()

        self.somef_output = self.read_temp_file()

        self.fair_output = {}

    def calculate_fairness(self):
        self.setup_header_info()
        self.fair_output["checks"] = []
        
        # add all checks functions
        self.evaluate_f1()
        self.evaluate_f1_2()
        self.evaluate_f2()

        # TODO: calculate fairness
        print("final output:")
        print(self.fair_output)

    def evaluate_f1(self):
        check = {"principle_id": "F1",
                 "category_id" : "Findable",
                 "title"       : "Software is assigned a globally unique and persistent identifier",
                 "description" : "This checks if there ir at least one DOI for this Software",
                 "total_passed_tests" : 0,
                 "total_tests_run"    : 0
                 }
        # test 1
        try:
            if len(self.somef_output["identifier"]) > 0:
                check["status"] = "ok"
                check["total_passed_tests"] += 1
                check["explanation"] = "A Digital Object Identifier (DOI) is assigned to the Software"
            else:
                raise
        except:
            check["status"] = "error"
            check["explanation"] = "No DOI assigned to the Software"
        check["total_tests_run"] += 1
        
        self.fair_output["checks"].append(check)

    def evaluate_f1_2(self):
        check = {"principle_id": "F1.2",
                 "category_id" : "Findable",
                 "title"       : "Different versions of the same software must be assigned distinct identifiers",
                 "description" : "This checks if every version has different and uniques identifiers",
                 "total_passed_tests": 0,
                 "total_tests_run"   : 0
                 }
        # test 1
        try:
            versions = []
            for v in self.somef_output["releases"]["excerpt"]:
                versions.append(v["tagName"])
        except:
            pass

        not_unique_versions = []
        for v in versions:
            count = versions.count(v)
            if count > 1 and v not in not_unique_versions:
                not_unique_versions.append(v)

        # need to check it
        if len(not_unique_versions) == 0 and len(versions) > 0:
            check["status"] = "ok"
            check["total_passed_tests"] += 1
            check["explanation"] = "Each version has a different identifier"
        elif len(not_unique_versions) > 0 and len(versions) > 0 :
            check["status"] = "error"
            check["explanation"] = "There are repeated identifiers (" + ",".join(not_unique_versions) + ")"
        else:
            check["status"] = "error"
            check["explanation"] = "No version identifiers found."
        check["total_tests_run"] += 1

        self.fair_output["checks"].append(check)
    
    def evaluate_f2(self):
        check = {"principle_id": "F2",
                 "category_id" : "Findable",
                 "title"       : "Software is described with rich metadata.",
                 "description" : "This check verifies if the the following minimum metadata [title, description, license, installation instructions, requirements, creator, creationDate] are present",
                 "total_passed_tests": 0,
                 "total_tests_run"   : 0
                 }

        # test 1 - check title
        title = []
        try:
            title.append(self.somef_output["longTitle"]["excerpt"])
        except: pass
        try:
            title.append(self.somef_output["name"]["excerpt"])
        except: pass
        try:
            title.append(self.somef_output["fullName"]["excerpt"])
        except: pass
            
        missing_metadata_error = "The following metadata are missing:"
        missing_metadata = []

        if len(title) > 1:
            check["total_passed_tests"] += 1
        else:
            missing_metadata.append("Title")
        check["total_tests_run"] += 1
        

        # TODO: description, license, installation instructions, requirements, creator, creationDate
        
        if len(missing_metadata) > 0:
            check["status"] = "error"
            missing_metadata_error += ", ".join(missing_metadata)
            check["explanation"] = missing_metadata_error
        else:
            check["status"] = "ok"
            check["explanation"] = "The software contains the following metadata [title, description, license, installation instructions, requirements, creator, creationDate]"

        self.fair_output["checks"].append(check)

    def generate_temp_file_name(self):
        name = self.repoURL

        remove_pattern = ["https://", "http://", "www.", "github.com"]
        for p in remove_pattern:
            name = name.replace(p,"")

        self.tmp_file =  name.rstrip('/').lstrip('/').replace('/','_') +  '.json'
        return self.tmp_file

    def read_temp_file(self):
        with open(self.tmp_file) as f:
            return json.load(f)

    def setup_header_info(self):
        # add url
        self.fair_output["software_repo_path"] = self.repoURL
        
        # add name
        try:
            self.fair_output["software_title"] = self.somef_output["longTitle"]["excerpt"]
        except:
            try:
                self.fair_output["software_title"] = self.somef_output["name"]["excerpt"]
            except:
                try:
                    self.fair_output["software_title"] = self.somef_output["fullName"]["excerpt"]
                except:
                    self.fair_output["software_title"] = ""

        # add license
        try:
            self.fair_output["license"] = self.somef_output["license"]["excerpt"]["url"]
        except:
            self.fair_output["license"] = ""
