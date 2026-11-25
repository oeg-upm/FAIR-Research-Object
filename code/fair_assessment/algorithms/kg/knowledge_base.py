import logging
from rdflib import Graph, Namespace, URIRef
from pathlib import Path
from rdflib.namespace import DCTERMS
import os

logger = logging.getLogger(__name__)

FTR = Namespace("https://w3id.org/ftr#")

logger.info("Load Algorithm description")
tests_graph = Graph()
tests_graph.parse("fair_assessment/algorithms/descriptions/FAIROS_DATASET_FUJI.ttl", format="turtle")


TESTS_DIRECTORY = Path(
    os.environ["TESTS_DIRECTORY"]
)

tests_directories = [os.environ["TESTS_DIRECTORY"]]

# Recursively find and load all .ttl files of tests
logger.info("Loading test description files")
for directory in tests_directories:
    for ttl_file in Path(directory).rglob("*.ttl"):
        logger.info(f"Loading {ttl_file}...")
        tests_graph.parse(ttl_file, format="turtle")

logger.info(f"Loaded {len(tests_graph)} triples from all TTL files.")

def get_description(test_uri):
    return tests_graph.value(subject=URIRef(test_uri), predicate=DCTERMS.description)

def get_title(test_uri):
    return tests_graph.value(subject=URIRef(test_uri), predicate=DCTERMS.title)