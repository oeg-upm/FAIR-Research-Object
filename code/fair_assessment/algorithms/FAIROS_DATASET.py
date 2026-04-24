import logging
from FAIROS_DATASET_FUJI import FAIROS_DATASET_FUJI
from FAIROS_DATASET_ROCRATE import FAIROS_DATASET_ROCRATE
import json
from datetime import datetime, UTC
import random

logger = logging.getLogger(__name__)

class FAIROS_DATASET:
    def execute_algorithm(self, resource, ticket):
        logger.info("Executing tests on dataset")

        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        random_suffix = random.randint(100, 999)
        resource_code = f"{timestamp}-{random_suffix}"

        assessment_code = f"{ticket}--{resource_code}"

        fuji = FAIROS_DATASET_FUJI()
        #Execute algorithm for F-UJI
        fuji_tests_results = fuji.execute_algorithm(resource,assessment_code)

        #Execute algorithm for rocrate
        rocrate = FAIROS_DATASET_ROCRATE()
        rocrate_tests_results = rocrate.execute_algorithm(resource, assessment_code)

        tests_results = self.integrate(fuji_tests_results, rocrate_tests_results)

        logger.info("Generating file assessment-results-"+str(assessment_code)+" with "+str(resource)+ "assessment")

        # Write the JSON-LD to a file
        output_file_results = f"C:\\Users\\egonzalez\\FAIROS\\assessments\\assessment-results-{assessment_code}.jsonld"
        with open(output_file_results, "w", encoding="utf-8") as f:
            json.dump(tests_results, f, ensure_ascii=False, indent=2)

        return tests_results

    def integrate(self,test_results1, tests_results2):
        test1_members = test_results1.get("hadMember", [])
        test2_members = tests_results2.get("hadMember", [])

        test_results1["hadMember"] = test1_members + test2_members

        return test_results1

         
