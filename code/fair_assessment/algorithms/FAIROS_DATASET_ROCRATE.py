import logging
from rdflib import Graph, Namespace, URIRef
from pathlib import Path
import validators
from datetime import datetime, timezone
from rdflib.namespace import DCTERMS
from kg.knowledge_base import get_title, get_description

logger = logging.getLogger(__name__)

class FAIROS_DATASET_ROCRATE:

    mappings={
        "Identifier is resolvable":"https://w3id.org/FAIROS/test/ROCRATE-F1-01",
        "metadata [title, description, publicationDate, summary,keywords] in ro-crate-metadata file":"https://w3id.org/FAIROS/test/ROCRATE-F2-01",
        "Metadata fields contentSize & encodingFormat founded":"https://w3id.org/FAIROS/test/ROCRATE-F3-01",
        "Metadata uses semantic resources":"https://w3id.org/FAIROS/test/ROCRATE-I2-01",
        "Metadata contains elements which hold provenance information and can be mapped to PROV (author and datePublished metadata found)":"https://w3id.org/FAIROS/test/ROCRATE-R1.2-01"
    }

    def execute_algorithm(self, rocrate_dataset, ticket):
        
        logger.info("Exploring rocrate metadata fields")

         # Current UTC time
        now = datetime.now(timezone.utc)
        formatted = now.strftime("%a %b %d %H:%M:%S UTC %Y")

        doc = {
            "@context": "https://w3id.org/ftr/context",
            "@id": f"urn:fairos:{ticket}",
            "@type": "https://w3id.org/ftr#TestResultSet",
            "description": (
                    "Set of test results that includes all tests included "
                    "in the Algorithm FAIROS_DATASET"
            ),
            "identifier": {
                "@id": f"urn:fairos:{ticket}"
            },
            "assessmentTarget": {
                "@id": f"{rocrate_dataset['@id']}"
            },
            "license": {
                "@id": "http://creativecommons.org/licenses/by/4.0/"
            },
            "title": "Results from running FAIROS DATASETS!",
            "generatedAtTime": {
                "@type": "http://www.w3.org/2001/XMLSchema#date",
                "@value": f"{formatted}"
            },
            "hadMember":[]
        }

        results = self.get_results_from_rocrate(rocrate_dataset)

        test_index = 0
        for explanation in results:
            test_index = test_index + 1
            if ":" in explanation:
                #The result is an string with PASS: test_name or FAIL: test_name
                value, test_text = explanation.split(':', 1)
                test_text = test_text.strip()
                logger.info("Test:"+str(test_text))
                test_uri = self.mappings.get(test_text)
                code = f"002"
                test_id = f"{ticket}-{code}-{test_index}"

                if test_uri:
                    description = get_description(test_uri)
                    title = get_title(test_uri)

                    if title is None:
                        print(f"{test_uri} with not title")

                    test = {
                        "@id": f"urn:fairos:{ticket}",
                        "@type": "https://w3id.org/ftr#TestResult",
                        "description": f"{description}",
                        "identifier": {
                            "@id": f"urn:fairos:{ticket}"
                        },
                        "assessmentTarget": {
                            "@id": f"{rocrate_dataset['@id']}"
                        },
                        "outputFromTest": {
                            "@id": f"{test_uri}",
                            "@type": "Test"
                        },
                        "license": {
                            "@id": "http://creativecommons.org/licenses/by/4.0/"
                        },
                        "title": f"{title}",
                        "value": f"{value}",
                        "completion": {
                            "@value": 100
                        },
                        "log": "N/A"
                    }
                                
                    doc["hadMember"].append(test)
                else:
                    logger.error(f"Invalid test url:{test_uri}")
        
        return doc

    def get_results_from_rocrate(self,rocrate_dataset):

        F2_1_1_message = "metadata [title, description, publicationDate, summary,keywords] in ro-crate-metadata file"
        F2_1_2_message = "metadata [creator, autor] in ro-crate-metadata file"

        explanations = []

        #Check F1.1
        explanations.append("PASS: Identifier is resolvable")
        
        #Check F1.2
        explanations.append("PASS: Identifier follows a defined persistent identifier syntax")
        explanations.append("PASS: Persisten identifier is resolvable")

        #Check F2.1
        if all(key in rocrate_dataset for key in ('title', 'description','publicationDate', 'summary', 'keywords')):
            explanations.append("PASS: " +F2_1_1_message)
        else:
            explanations.append("FAIL: "+F2_1_1_message)

        if all(key in rocrate_dataset for key in ('publisher', 'creator')):
            explanations.append("PASS: " +F2_1_2_message)
        else: 
            explanations.append("FAIL: " +F2_1_2_message)
        
        #Check F3.1
        if all(key in rocrate_dataset for key in ('contentSize', 'encodingFormat')):
            explanations.append("PASS: Metadata fields contentSize & encodingFormat founded")
        else:
            explanations.append("FAIL: Metadata fields contentSize & encodingFormat founded")
            
        if all(key in rocrate_dataset for key in ('dataDistribution')):
            explanations.append("PASS: Metadata field dataDistribution found")
        else:
            explanations.append("FAIL: Metadata field dataDistribution found")
        
        #Check F4.1
        explanations.append("PASS: Metadata is in JSON-LD format")

        #Check A1.1
        if all(key in rocrate_dataset for key in ('copyrightHolder')):
            explanations.append("PASS: Data access information is machine readable (copyrightHoder metadata)")
        else:
            explanations.append("FAIL: Data access information is machine readable (copyrightHoder metadata)")

        #Check A1.2
        explanations.append("PASS: Landing page link is based on standardized web communication protocols.")
            
        #Check A1.3
        if all(key in rocrate_dataset for key in ('dataDistribution')):
            explanations.append("PASS: downloaded link found (dataDistribution metadata found)")
        else:
            explanations.append("FAIL: downloaded link found (dataDistribution metadata found)")
       
        #Check I1.1
        explanations.append("PASS: Metadata in JSON-LD format")
        
        #Check I1.2
        explanations.append("PASS: Metadata uses semantic resources")
        
        #Check I3.1
        explanations.append("PASS: Resource is mentioned in the metadata (hasPart relation)")
        explanations.append("PASS: Resource is mentioned with a machine readable link (@id metadata)")
        
        #Check R1.1
        if 'encodingFormat' in rocrate_dataset:
            explanations.append("PASS: Resource type is given in metadata (encondingFormat metadata found")
        else:
            explanations.append("FAIL: Resource type is given in metadata (encondingFormat metadata found")
        
        if 'encodingFormat' in rocrate_dataset:
            explanations.append("PASS: Information about data content (e.g. links) is given in metadata (encondingFormat metadata found")
        else:
            explanations.append("FAIL: Information about data content (e.g. links) is given in metadata (encondingFormat metadata found")
            
        if 'contentSize' in rocrate_dataset and 'encodingFormat' in rocrate_dataset:
            explanations.append("PASS: File size and type information are specified in metadata (contentSize and encondingFormat metadata found")
        else:
            explanations.append("FAIL: File size and type information are specified in metadata (contentSize and encondingFormat metadata found")

        if 'contentSize' in rocrate_dataset and 'encodingFormat' in rocrate_dataset:
            explanations.append("PASS: Measured variables or observation types are specified in metadata (contentSize and encondingFormat metadata found")
        else:
            explanations.append("FAIL: Measured variables or observation types are specified in metadata (contentSize and encondingFormat metadata found")
            
        explanations.append("FAIL: Data content matches file type and size specified in metadata")
        explanations.append("FAIL: Data content matches measured variables or observation types specified in metadata")
        
        #Check R1.1.1
        if all(key in rocrate_dataset for key in ('copyrightHolder')):
            explanations.append("PASS: Licence information is given in an appropriate metadata element (copyrightHoder metadata)")
            explanations.append("FAIL: Recognized licence is valid and registered at SPDX")
        else:
            explanations.append("FAIL: Licence information is given in an appropriate metadata element (copyrightHoder metadata)")
            explanations.append("FAIL: Recognized licence is valid and registered at SPDX")
        
        #Check R1.2.1
        if all(key in rocrate_dataset for key in ('author','datePublished')):
            explanations.append("PASS: Metadata contains elements which hold provenance information and can be mapped to PROV (author and datePublished metadata found)")
            explanations.append("FAIL: Metadata contains provenance information using formal provenance ontologies (PROV-O)")
        else:
            explanations.append("FAIL: Metadata contains elements which hold provenance information and can be mapped to PROV (author and datePublished metadata not found)")

        #Check R1.3.1
        explanations.append("PASS: Metadata follows a standard recommended by the target research community of the data. -> (rocrate specification)")
       
        #Check R1.3.2
        if "encodingFormat" in rocrate_dataset:
            if rocrate_dataset["encodingFormat"] in ["ASCII", "image/png", "csv", "json"]:
                explanations.append("PASS: type has an open format") 
            else:
                explanations.append("FAIL: type has an open format")

        return explanations
