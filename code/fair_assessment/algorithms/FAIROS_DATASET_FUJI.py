import logging
import traceback
from rocrate.rocrate import ROCrate
import validators
from fuji_wrapper.fujiwrapper import FujiWrapper
from rdflib import Graph, Namespace, URIRef
import json
from datetime import datetime, timezone
from pathlib import Path
from rdflib.namespace import DCTERMS
from kg.knowledge_base import get_title, get_description

logger = logging.getLogger(__name__)

class FAIROS_DATASET_FUJI:

    mappings={
        "Identifier is resolvable and follows a defined unique identifier syntax (IRI, URL)":"https://w3id.org/FAIROS/test/FUJI-F1-01",
        "Identifier follows a defined persistent identifier syntax":"https://w3id.org/FAIROS/test/FUJI-F1-02",
        "Metadata includes descriptive core elements (creator, title, data identifier, publisher, publication date, summary and keywords) to support data findability.":"https://w3id.org/FAIROS/test/FUJI-F2-02",
        "Metadata has been made available via common web methods":"https://w3id.org/FAIROS/test/FUJI-F4-01",
        "Core data citation metadata is available":"https://w3id.org/FAIROS/test/FUJI-F2-01",
        "Core descriptive metadata is available":"https://w3id.org/FAIROS/test/FUJI-F2-02",
        "Metadata includes the identifier of the data it describes.":"https://w3id.org/FAIROS/test/FUJI-F3-01",
        "Metadata contains a PID or URL which indicates the location of the downloadable data content":"https://w3id.org/FAIROS/test/FUJI-F3-01",
        "Metadata is given in a way major search engines can ingest it for their catalogues (embedded JSON-LD, Dublin Core or RDFa)":"https://w3id.org/FAIROS/test/FAIR-I1-01",
        "Information about access restrictions or rights can be identified in metadata":"https://w3id.org/FAIROS/test/FUJI-A1-01",
        "Metadata is accessible through a standardized communication protocol.":"https://w3id.org/FAIROS/test/FUJI-A1-02",
        "Data access information is indicated by (not machine readable) standard terms":"https://w3id.org/FAIROS/test/FUJI-A1-03",
        "Parsable, structured metadata (JSON-LD, RDFa) is embedded in the landing page XHTML/HTML code":"https://w3id.org/FAIROS/test/FUJI-I1-01",
        "Parsable, graph data (RDF, JSON-LD) is accessible through content negotiation, typed links or sparql endpoint":"https://w3id.org/FAIROS/test/FUJI-I1-02",
        "Metadata uses semantic resources":"https://w3id.org/FAIROS/test/FUJI-I1-02",
        "Vocabulary namespace URIs can be identified in metadata":"https://w3id.org/FAIROS/test/FUJI-I2-01",
        "Metadata includes links between the data and its related entities.":"https://w3id.org/FAIROS/test/FUJI-I3-01",
        "Related resources are indicated by machine readable links or identifiers":"https://w3id.org/FAIROS/test/FUJI-I3-02",
        "Minimal information about available data content is given in metadata":"https://w3id.org/FAIROS/test/FUJI-R1-01",
        "Information about data content (e.g. links) is given in metadata":"https://w3id.org/FAIROS/test/FUJI-R1-02",
        "Data content matches measured variables or observation types specified in metadata":"https://w3id.org/FAIROS/test/FUJI-R1-03",
        "Licence information is given in an appropriate metadata element":"https://w3id.org/FAIROS/test/FUJI-R1.1-01",
        "Metadata contains elements which hold provenance information and can be mapped to PROV":"https://w3id.org/FAIROS/test/FUJI-R1.2-01",
        "Metadata contains provenance information using formal provenance ontologies (PROV-O)":"https://w3id.org/FAIROS/test/FUJI-R1.2-02",
        "Multidisciplinary but community endorsed metadata (RDA Metadata Standards Catalog, fairsharing) standard is listed in the re3data record or detected by namespace":"https://w3id.org/FAIROS/test/FUJI-R1.3-01",
        "The format of a data file given in the metadata is listed in the long term file formats, open file formats or scientific file formats controlled list":"https://w3id.org/FAIROS/test/FUJI-R1.3-02"
    }

    def execute_algorithm_uri(self, resource_uri, ticket):
       
        logger.info("Invoking F-UJI")

        fuji = FujiWrapper(resource_uri)

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
                "@id": f"{resource_uri}"
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

        #Get results from f-uji
        results_json = fuji.get_checks()

        #Explore results, divided in metrics
        for item in results_json:
            explanations = []
            for src in item.get("sources", []):
                explanations.extend(src.get("explanation", []))
                #Each explanation is a test results
                test_index = 0
                for explanation in explanations:
                    test_index = test_index + 1
                    if ":" in explanation:
                        #The result is an string with PASS: test_name or FAIL: test_name
                        value, test_text = explanation.split(':', 1)
                        test_text = test_text.strip()

                        test_uri = self.mappings.get(test_text)
                        code = f"001"
                        test_id = f"{ticket}-{code}-{test_index}"

                        if test_uri:
                            description = get_description(test_uri)
                            title = get_title(test_uri)

                            test = {
                                "@id": f"urn:fairos:{test_id}",
                                "@type": "https://w3id.org/ftr#TestResult",
                                "description": f"{description}",
                                "identifier": {
                                    "@id": f"urn:fairos:{test_id}"
                                },
                                "assessmentTarget": {
                                    "@id": f"{resource_uri}"
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
                        logger.error(f"Invalid format for explanation:{explanation}")

        return doc   

    def execute_algorithm(self, rocrate_dataset, ticket):
       
        logger.info("Invoking F-UJI")

        if validators.url(rocrate_dataset["@id"]):
            fuji = FujiWrapper(rocrate_dataset["@id"])

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

            #Get results from f-uji
            results_json = fuji.get_checks()

            #Explore results, divided in metrics
            for item in results_json:
                explanations = []
                for src in item.get("sources", []):
                    explanations.extend(src.get("explanation", []))
                    #Each explanation is a test results
                    test_index = 0
                    for explanation in explanations:
                        test_index = test_index + 1
                        if ":" in explanation:
                            #The result is an string with PASS: test_name or FAIL: test_name
                            value, test_text = explanation.split(':', 1)
                            test_text = test_text.strip()

                            test_uri = self.mappings.get(test_text)
                            code = f"001"
                            test_id = f"{ticket}-{code}-{test_index}"

                            if test_uri:
                                description = get_description(test_uri)
                                title = get_title(test_uri)

                                test = {
                                    "@id": f"urn:fairos:{test_id}",
                                    "@type": "https://w3id.org/ftr#TestResult",
                                    "description": f"{description}",
                                    "identifier": {
                                        "@id": f"urn:fairos:{test_id}"
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
                            logger.error(f"Invalid format for explanation:{explanation}")
            logger.info("Assessment document generated")
            return doc