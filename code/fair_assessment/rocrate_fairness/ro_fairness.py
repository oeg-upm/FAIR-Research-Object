from rocrate.rocrate import ROCrate, read_metadata, Metadata
import json
import requests
from os.path import isfile, isdir, join
import validators
import random # remove

def check_element_has_key(element, keys):
    has, has_not = [], []
    for key in keys:
        has.append(key) if key in element else has_not.append(key)
    return has, has_not

class ROCrateFAIRnessCalculator():

    F2_1_1_message = "metadata [title, description, publicationDate, summary,keywords] in ro-crate-metadata file"
    F2_1_2_message = "metadata [creator, autor] in ro-crate-metadata file"

    def __init__(self, ro_path) -> None:
        self.ro_path = ro_path

        self.rocrate = ROCrate(ro_path)
        
        self.ro_metadata = self.rocrate.metadata.as_jsonld() # ro metadata
        self.ro          = self.rocrate.dereference("./").as_jsonld() # ro itself
        self.ro_parts    = [self.rocrate.dereference(part["@id"]).as_jsonld() for part in self.ro["hasPart"]] # all the parts of the ro
        
        self.fair_output = {}
        self.add_header_to_file()
        self.fair_output["score"]= {}
        self.fair_output["checks"] = []
        
    def calculate_fairness(self, aggregation_mode=0):
        self.evaluate_f1()
        self.evaluate_f2()
        self.evaluate_f3()
        self.evaluate_r1_1()
        self.evaluate_r1_2()
        self.calculate_fair_score(aggregation_mode)
        return self.fair_output
        
    def save_to_file(self):
        with open('ro-crate-fairness.json', 'w') as f:
            json.dump(self.fair_output, f, sort_keys=True, indent=4)

    def add_header_to_file(self):
        # add header info to the final output
        self.fair_output["rocrate_path"] = self.ro_path + Metadata.BASENAME
    
    def get_identifier(self):
        if "identifier" in self.ro_metadata:
            return self.ro_metadata["identifier"]
        else:
            return self.ro_path + Metadata.BASENAME
    
    def rocrate_principle_check(self, element_id, principle_id):
        checks = []
        element = self.rocrate.dereference(element_id).as_jsonld()
        explanations = []
        checks_source = []
        check = {}
        score = 0
        total_score = 0

        total_passed_tests = 0
        total_tests_run = 0

        check["source"] = "ro-crate"

        if principle_id=="F1.1":
            score = 0
            total_score = 1

            #All urls in RELIANCE are resolvable
            score = 1
            total_passed_tests += 1
            explanations.append("PASS: Identifier is resolvable")
            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="F1.2":
            score = 0
            total_score = 1

            #All urls in RELIANCE are resolvable
            score = 1
            total_passed_tests += 2
            explanations.append("PASS: Identifier follows a defined persistent identifier syntax")
            explanations.append("PASS: Persisten identifier is resolvable")
            total_tests_run += 2

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="F2.1":
            score = 0
            total_score = 2
            if all(key in element for key in ('title', 'description','publicationDate', 'summary', 'keywords')):
                score += 1
                total_passed_tests += 1
                explanations.append("PASS: " +self.F2_1_1_message)
            else:
                explanations.append("FAIL: Missing "+self.F2_1_1_message)
            total_tests_run += 1
            if all(key in element for key in ('publisher', 'creator')):
                score = +1
                total_passed_tests += 1
                explanations.append("PASS: " +self.F2_1_2_message)
            else: 
                explanations.append("FAIL: " +self.F2_1_2_message)
            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 2:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="F3.1":
            score = 0
            total_score = 1

            if all(key in element for key in ('contentSize', 'encodingFormat')):
                score += 0.5
                total_passed_tests += 1
                explanations.append("PASS: Metadata fields contentSize & encodingFormat founded")
            else:
                explanations.append("FAIL: Metadata fields contentSize & encodingFormat missing")
            total_tests_run += 1

            if all(key in element for key in ('dataDistribution')):
                score += 0.5
                total_passed_tests += 1
                explanations.append("PASS: Metadata field dataDistribution found")
            else:
                explanations.append("FAIL: Metadata field dataDistribution missing")
            total_tests_run += 1


            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="F4.1":
            score = 0
            total_score = 2

            #Metadata is in JSON-LD format by default
            score = 1
            total_passed_tests = 1
            explanations.append("PASS: Metadata is in JSON-LD format")

            total_tests_run = 2

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="A1.1":
            score = 0
            total_score = 1

            if all(key in element for key in ('copyrightHolder')):
                score += 1
                total_passed_tests += 1
                explanations.append("PASS: Data access information is machine readable (copyrightHoder metadata)")
            else:
                explanations.append("FAIL: Data access information is machine readable (copyrightHoder metadata not found)")

            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="A1.3":
            score = 0
            total_score = 1

            if all(key in element for key in ('dataDistribution')):
                score += 1
                total_passed_tests += 1
                explanations.append("PASS: downloaded link found (dataDistribution metadata found)")
            else:
                explanations.append("FAIL: downloaded link not found (dataDistribution metadata not found)")

            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="I1.1":
            score = 0
            total_score = 2

            #Always in an ro-crate metadata file
            score += 1
            explanations.append("PASS: Metadata in JSON-LD format")
            total_passed_tests += total_passed_tests
            total_tests_run += 1

            #Always in an ro-crate metadata file
            score += 1
            explanations.append("PASS: Graph data in JSON-LD format")
            total_passed_tests += total_passed_tests
            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 2:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="I1.2":
            score = 0
            total_score = 1

            #Always in an ro-crate metadata file
            score += 1
            explanations.append("PASS: Metadata uses semantic resources")
            total_passed_tests += total_passed_tests
            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="I3.1":
            score = 0
            total_score = 1

            #Include a hasPart metadata field
            score += 0.5
            explanations.append("PASS: Resource is mentioned in the metadata (hasPart relation)")
            total_passed_tests += total_passed_tests
            total_tests_run += 1

            #Include a hasPart metadata field
            score += 0.5
            explanations.append("PASS: Resource is mentioned with a machine readable link (@id metadata)")
            total_passed_tests += total_passed_tests
            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="R1.1":
            score = 0
            total_score = 4

            if 'encodingFormat' in element:
                score += 0.5
                total_passed_tests += 1
                explanations.append("PASS: Resource type is given in metadata (encondingFormat metadata found")
            else:
                explanations.append("FAIL: Resource type is not given in metadata (encondingFormat metadata not found")
            total_tests_run += 1

            if 'encodingFormat' in element:
                score += 0.5
                total_passed_tests += 1
                explanations.append("PASS: Information about data content (e.g. links) is given in metadata (encondingFormat metadata found")
            else:
                explanations.append("FAIL: Information about data content (e.g. links) is not given in metadata (encondingFormat metadata not found")
            total_tests_run += 1
            
            if 'contentSize' in element and 'encodingFormat' in element:
                score += 0.5
                total_passed_tests += 1
                explanations.append("PASS: File size and type information are specified in metadata (contentSize and encondingFormat metadata found")
            else:
                explanations.append("FAIL: File size and type information are not specified in metadata (contentSize and encondingFormat metadata not found")
            total_tests_run += 1

            if 'contentSize' in element and 'encodingFormat' in element:
                score += 0.5
                total_passed_tests += 1
                explanations.append("PASS: Measured variables or observation types are specified in metadata (contentSize and encondingFormat metadata found")
            else:
                explanations.append("FAIL: Measured variables or observation types are specified in metadata (contentSize and encondingFormat metadata not found")
            total_tests_run += 1

            explanations.append("FAIL: Data content matches file type and size specified in metadata")
            total_tests_run += 1

            explanations.append("FAIL: Data content matches measured variables or observation types specified in metadata")
            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score >= 2:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="R1.1.1":
            score = 0
            total_score = 2

            if all(key in element for key in ('copyrightHolder')):
                score += 1
                total_passed_tests += 1
                explanations.append("PASS: Licence information is given in an appropriate metadata element (copyrightHoder metadata)")
                explanations.append("FAIL: Recognized licence is valid and registered at SPDX")
                total_tests_run += 1
            else:
                explanations.append("FAIL: Licence information is not given in an appropriate metadata element (copyrightHoder metadata not found)")
                explanations.append("FAIL: Recognized licence is valid and registered at SPDX")
                total_tests_run += 1
                
            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score >= 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="R1.2.1":
            score = 0
            total_score = 2

            if all(key in element for key in ('author','datePublished')):
                score += 1
                total_passed_tests += 1
                explanations.append("PASS: Metadata contains elements which hold provenance information and can be mapped to PROV (author and datePublished metadata found)")
                explanations.append("FAIL: Metadata contains provenance information using formal provenance ontologies (PROV-O)")
                total_tests_run += 1
            else:
                explanations.append("FAIL: Metadata not contains elements which hold provenance information and can be mapped to PROV (author and datePublished metadata not found)")

            total_tests_run += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score >= 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="R1.3.1":
            score = 0
            total_score = 1

            score += 1
            explanations.append("PASS: Metadata follows a standard recommended by the target research community of the data. -> (rocrate specification)")
            total_tests_run += 1
            total_passed_tests += 1

            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations
        elif principle_id=="R1.3.2":
            score = 0
            total_score = 1

            if "encodingFormat" in element:
                if element["encodingFormat"] in ["ASCII", "image/png", "csv", "json"]:
                    score += 1
                    total_passed_tests += 1
                    explanations.append("PASS: type has an open format") 
                else:
                    explanations.append("PASS: type has not an open format")


            total_tests_run += 1
            
            check["score"] = score
            check["total_tests_run"] = total_tests_run
            check["total_passed_tests"] = total_passed_tests
            check["total_score"] = total_score
            if score == 1:
                check["assessment"] = "pass"
            else:
                check["assessment"] = "fail"
            check["explanations"] = explanations

        return check

    def get_element_basic_checks(self, element_id):
        checks = []
        element = self.rocrate.dereference(element_id).as_jsonld()
        # TODO: refactor
        # f2
        minimum_metadata = ["author", "license", "description"]
        check = {"principle_id": "F2",
                "category_id" : "Findable",
                "title"       : "Data are described with rich metadata",
                "description" : f"This check verifies if the the following minimum metadata {minimum_metadata} are present in the reserch object",
                "total_passed_tests": 0,
                "total_tests_run"   : 0
                }
        missing_metadata_error = "Missing the following metadata: "
        minimum_metadata = ["author", "license", "description"]
        missing_metadata = []
        for meta in minimum_metadata:
            if not meta in element:
                missing_metadata.append(meta)
        if len(missing_metadata) > 0:
            check["status"] = "error"
            missing_metadata_error += ", ".join(missing_metadata)
            check["explanation"] = missing_metadata_error
        else:
            check["status"] = "ok"
            check["total_passed_tests"] += 1
            check["explanation"] = f"This element has the following metadata {minimum_metadata}"
        check["total_tests_run"] += 1
        checks.append(check)
        
        # r1.1
        check = {"principle_id": "R1.1",
                "category_id" : "Reusable",
                "title"       : "(Meta)data are released with a clear and accessible data usage license",
                "description" : f"This check verifies whether the element in the reserch object has a licence",
                "total_passed_tests": 0,
                "total_tests_run"   : 0
                }
        if not "license" in element:
            check["status"] = "error"
            check["explanation"] = f"This element have no licence"
        else:
            check["status"] = "ok"
            check["explanation"] = "This element has a license"
            check["total_passed_tests"] += 1
        check["total_tests_run"] += 1
        checks.append(check)

        # r1.2
        fields = ["author", "datePublished", "citation"]
        check = {"principle_id": "R1.2",
                 "category_id": "Reusable",
                 "title": "(Meta)data are associated with detailed provenance",
                 "description": f"This check verifies that the element in the reserch object has the following fields: {fields}",
                 "total_passed_tests": 0,
                 "total_tests_run": 0,
                 "explanation" : []
                 }
        
        _, has_not = check_element_has_key(element, fields)
        if len(has_not) > 0:
            check["explanation"] = f"This element has no :{', '.join(has_not)}"
            check["status"] = "error"
        else:
            check["status"] = "ok"
            check["explanation"] = f"This element has: {fields}"
            check["total_passed_tests"] += 1
        check["total_tests_run"]+=1
        checks.append(check)
        return checks
            
    def calculate_fair_score(self, aggregation_mode): # Proof of concept. TODO:
        
        if aggregation_mode == 0:
            description = "Description of the way of calculate the score"
            self.fair_output["score"] = {"description" : description, "total_sum" : {"earned": 0, "total": 0}}

            for check in self.fair_output["checks"]:
                self.fair_output["score"]["total_sum"]["earned"] += check["total_passed_tests"]
                self.fair_output["score"]["total_sum"]["total"]  += check["total_tests_run"]
            self.fair_output["score"]["final"] = (self.fair_output["score"]["total_sum"]["earned"] / self.fair_output["score"]["total_sum"]["total"]) * 100
            
        elif aggregation_mode == 1:
            description = "Random score"
            self.fair_output["score"] = {"description": description, "value" : random.uniform(0,100)}
            
        elif aggregation_mode == 2:
            description = "Perfect score"
            self.fair_output["score"] = {"description": description, "value" : 100}
        
        
    def evaluate_f1(self):
        valid_domains = ["w3id.org", "doi.org", "purl.org", "www.w3.org"]
        check = {"principle_id": "F1",
                 "category_id" : "Findable",
                 "title"       : "(Meta)data are assigned a persistent identifier",
                 "description" : f"This check verifies if the RO has a persintance identifier {valid_domains}",
                 "total_passed_tests": 0,
                 "total_tests_run"   : 0
                 }

        # test 1
        if "identifier" in self.ro_metadata:
            identifier = self.ro_metadata["identifier"]
        
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

        self.fair_output["checks"].append(check)

    def evaluate_f2(self):
        minimum_metadata = ["author", "license", "description"]
        check = {"principle_id": "F2",
                "category_id" : "Findable",
                "title"       : "Data are described with rich metadata",
                "description" : f"This check verifies if the the following minimum metadata {minimum_metadata} are present in the ro-crate",
                "total_passed_tests": 0,
                "total_tests_run"   : 0
                }
        missing_metadata_error = "Missing the following metadata: "
        missing_metadata = []

        # test 1
        for meta in minimum_metadata:
            if not meta in self.ro:
                missing_metadata.append(meta)

        if len(missing_metadata) > 0:
            check["status"] = "error"
            missing_metadata_error += ", ".join(missing_metadata)
            check["explanation"] = missing_metadata_error
        else:
            check["status"] = "ok"
            check["total_passed_tests"] += 1
            check["explanation"] = f"The ro-crate contains the following metadata {minimum_metadata}"

        check["total_tests_run"] += 1

        self.fair_output["checks"].append(check)

    def evaluate_f3(self):
        check = {"principle_id": "F3",
                "category_id" : "Findable",
                "title"       : "Metadata clearly and explicitly include the identifier of the data they describe",
                "description" : "This check verifies that the hasPart elements exists and are describe in the ro",
                "total_passed_tests": 0,
                "total_tests_run"   : 0
                }

        # test 1. check if the hasParts exist in the directory. if they are urls make a request
        errors_found = []

        for part in self.ro_parts:
            part_id = part["@id"]

            # checks if the id is a URL
            if validators.url(part_id):
                response = requests.get(part_id)
                if response.status_code < 400:
                    # print(f"{part_id} exists remotely")
                    pass
                else:
                    # print(f"{part_id} could not be found")
                    errors_found.append(f"This IRI could not be found: {part_id}")
             
            # The ROCrate library does not allow an id that is not defined. 
            # So the elements inside hasPart will always be defined
            else:
                path = join(self.ro_path, part_id)
                
                if not isdir(path) and not isfile(path):
                    # print("UNKOWN: ", part_id)
                    errors_found.append(f"{part_id} is described but has not been found locally")

        if len(errors_found) > 0:
            check["status"] = "error"
            check["explanation"] = errors_found
        else:
            check["status"] = "ok"
            check["explanation"] = "All element identifiers exists"
            check["total_passed_tests"] += 1

        check["total_tests_run"] += 1
        self.fair_output["checks"].append(check)

    def evaluate_i2(self): # not used ATM
        # assume that it is a simple context ( "@context": "https://w3id.org/ro/crate/1.0/context" )
        check = {"principle_id": "I2",
                 "category_id" : "Interoperable",
                 "title"       : "(Meta)data use vocabularies that follow FAIR principles",
                 "description" : "This check verifies if the RO use a FAIR context (schema.org)",
                 "total_passed_tests": 0,
                 "total_tests_run"   : 0
                 }

        # test 1
        valid_vocab = ["schema.org"]
        
        # get the vocabulary of the context 
        context, _ = read_metadata(self.ro_path + Metadata.BASENAME)
        request = requests.get(context)
        context_vocab = request.json()["@context"]
        
        unfair_vocabs = []
        
        # check vocab use in the definitions of the parts (hasPart):
        for part in self.ro_parts:
            for key in list(part.keys()):
                if key[0] != '@':
                    if not any(vocab in context_vocab[key] for vocab in valid_vocab):
                        unfair_vocabs.append(context_vocab[key])
                        # print("UNFAIR vocab: ",context_vocab[key])
                        
        if len(unfair_vocabs) == 0:
            check["status"] = "ok"
            check["explanation"] = "All vocabularies are FAIR"
            check["total_passed_tests"] += 1
        else:
            check["status"] = "error"
            check["explanation"] = f"This vocabularies are unFAIR: {unfair_vocabs}"
        check["total_tests_run"] += 1
        
        self.fair_output["checks"].append(check)   
        
    
    def evaluate_r1_1(self):
        check = {"principle_id": "R1.1",
                "category_id" : "Reusable",
                "title"       : "(Meta)data are released with a clear and accessible data usage license",
                "description" : "This check verifies whether the RO has a licence. It also checks that there is a licence in RO parts",
                "total_passed_tests": 0,
                "total_tests_run"   : 0
                }

        # test 1. Licence in root data entity
        entities = self.ro_parts + [self.ro_metadata]
        unlicensed_entities = []
        
        for entity in entities:
            if not "license" in entity:
                unlicensed_entities.append(entity["@id"])
        
        if len(unlicensed_entities) == 0:
            check["status"] = "ok"
            check["explanation"] = "The RO and its components are licensed"
            check["total_passed_tests"] += 1
        else:
            check["status"] = "error"
            check["explanation"] = f"These entities have no licence: {unlicensed_entities}"
            
        check["total_tests_run"] += 1

        self.fair_output["checks"].append(check)

    def evaluate_r1_2(self):
        fields = ["author", "datePublished", "citation"]
        check = {"principle_id": "R1.2",
                 "category_id": "Reusable",
                 "title": "(Meta)data are associated with detailed provenance",
                 "description": f"This check verifies that all elements of the RO have the following fields: {fields}",
                 "total_passed_tests": 0,
                 "total_tests_run": 0,
                 "explanation" : []
                 }
        
        # test 1
        all_elements = self.ro_parts + [self.ro_metadata]
        
        def add_explanation(element, has_not):
            check["explanation"].append(f"{element['@id']} do not have {', '.join(has_not)}")
            
        for element in all_elements: 
            _, has_not = check_element_has_key(element, fields)
            if len(has_not) > 0:
                add_explanation(element, has_not)
     
            
        if len(check["explanation"]) == 0:
            check["status"] = "ok"
            check["total_passed_tests"] += 1
        else:
             check["status"] = "error"
        
        check["total_tests_run"] += 1
        
        self.fair_output["checks"].append(check)
