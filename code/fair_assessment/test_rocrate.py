from rocrate.rocrate import ROCrate
from algorithms.FAIROS_DATASET_ROCRATE import FAIROS_DATASET_ROCRATE
import traceback
import json

rocrate_filename = f"C:\\Users\\egonzalez\\projects\\FAIR-Research-Object\\code\\service\\tests\\13dfbe3b-3132-4089-9ec9-5ae100fb143c"
ticket="fdsf88888fdfdf888"
rocrate = ROCrate(rocrate_filename)

try:
    rocrate = ROCrate(rocrate_filename)
    ro = rocrate.dereference("./").as_jsonld()  # ro itself
    ro_parts = [
        rocrate.dereference(part["@id"]).as_jsonld()
        for part in ro["hasPart"]
    ]

    for element in ro_parts:
        type = element["@type"]
        id = element["@id"]   
        if ("Dataset" in type and not "http://purl.org/wf4ever/wf4ever#Folder" in type) or "http://purl.org/wf4ever/wf4ever#Dataset" in type:   
            dataset = FAIROS_DATASET_ROCRATE()
            results=dataset.execute_algorithm(element, ticket)
            # Write the JSON-LD to a file
            with open("fairos_rocrate_results.jsonld", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

except Exception as ex:
    print(traceback.format_exc())