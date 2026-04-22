import logging
import traceback
from rocrate.rocrate import ROCrate
import os, sys
from datetime import datetime, timezone
import json

sys.path.insert(0, os.path.dirname(__file__))
from FAIROS_DATASET import FAIROS_DATASET

logger = logging.getLogger(__name__)

class FAIROS:


    def execute_algorithm(rocrate_filename, ticket):
        # Current UTC time
        value = 0.0
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
                "@id": f"{rocrate_filename}"
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

        percentages = []
        log_entries = []

        logging.info(f"Exploring rocrate file {rocrate_filename}")

        try:
            rocrate = ROCrate(rocrate_filename)
            ro = rocrate.dereference("./").as_jsonld()  # ro itself
            doc["assessmentTarget"]=ro["identifier"]
            ro_parts = [
                rocrate.dereference(part["@id"]).as_jsonld()
                for part in ro["hasPart"]
            ]
            logging.info(f"{len(ro_parts)} resources detected in the RO")
            for element in ro_parts:
                log_value=""
                type = element["@type"]
                id = element["@id"]   
                if ("Dataset" in type and not "http://purl.org/wf4ever/wf4ever#Folder" in type) or "http://purl.org/wf4ever/wf4ever#Dataset" in type:   
                    logger.info(f"Resource detected as Dataset: {id}")
                    dataset = FAIROS_DATASET()
                    result_testset = dataset.execute_algorithm(element, ticket)
                    doc["hadMember"] = doc["hadMember"]+result_testset["hadMember"]
                    
                    percentage = 0
                    total = len(result_testset["hadMember"])
                    if total != 0:
                        passed = sum(
                            1 for test in result_testset["hadMember"]
                            if test.get("value") == "PASS"
                        )
                        percentage = (passed / total) * 100

                    percentages.append(percentage)
                    log_entries.append({
                        "@id": id,
                        "passed": passed if total != 0 else 0,
                        "total": total,
                        "percentage": percentage
                    })

            if percentages:
                value = sum(percentages) / len(percentages)
            else:
                value = 0.0

            log_value = json.dumps(log_entries, ensure_ascii=False)

            logger.info("Generating file assessment-results-"+str(ticket))

            # Write the JSON-LD to a file
            output_file_results = f"C:\\Users\\egonzalez\\tests_results\\assessment-results-{ticket}.jsonld"
            with open(output_file_results, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)

            score = {
                "@context": "https://w3id.org/ftr/context",
                "@id": f"urn:fairos:{ticket}",
                "@type": "https://w3id.org/ftr#BenchmarkScore",
                "value": f"{value}",
                "log": f"{log_value}",
                "scoredTestResults": doc["hadMember"]
            }

            # Write the JSON-LD to a file
            output_file_score = f"C:\\Users\\egonzalez\\tests_results\\score-{ticket}.jsonld"
            with open(output_file_score, "w", encoding="utf-8") as f:
                json.dump(score, f, ensure_ascii=False, indent=2)

        except Exception as ex:
            logger.error("Error to load rocrate file")
            print(traceback.format_exc())

    
    def get_id():
        return "FAIROS"
    def getTTL():
        return "simple"
    