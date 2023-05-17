## Output Assessment JSON format

**Version** : 1.0.0

The structure of the JSON output from the assessment is as following

```json
{

  "components": [

  …

  ],

  "overall\_score": {

  "description": "Formula: score of each principle / total score",

  "score": 51.04

  }

}
```

The first element of the JSON is a collection of the class \<Component\>.

The second element is an overall score of the Research Object. This score is calculated based on the partial scores. For the moment we used the policy defined in the description file.

| Property | Mandatory | Expected value | Definition |
| --- | --- | --- | --- |
| description | Yes | String | Description of the policy used to calculate the overall score |
| score | Yes | Number | Value of the score |

### Component

A Research Object is composed of a collection of components/resources. Each component represents a digital object of the Research Object.

In a ro-crate metadata file, the first component is the Research Object itself, it means, the assessment of the metadata of the Research Object using the tool F-UJI. Note that this structure is the same in the rest of the RO resources

```json
{

  "name": "Global Water Watch using OpenEO on C-Scale",

  "identifier": "https://w3id.org/ro-id/813ac793-f4ba-46d1-9d5e-6552227de7a0",

  "type": "ro-crate",

  "tool-used": [

  "F-uji",

  "ro-crate-metadata"

  ],

  "checks": [

  …

  ],

  "score": {

  …

  }

}

```

| Property | Mandatory | Expected value | Definition |
| --- | --- | --- | --- |
| name | Yes | String | Title of the RO present in the ro-crate metadata file. |
| identifier | Yes | String | String that identifies the RO in the metadata file. Normally is assigned by the tool used to publish the RO |
| type | Yes | Enumerate(ro-crate | software | dataset | ontology) | Represent the nature of the component. Ro-crate represent the RO itself (those metadata associated directly to the RO, not to the components) |
| tool-used | Yes | Enumerate(ro-crate-metaF-UJI | somef | foops) | Ro-crate-metadata is an internal tool to complement the assessment of the F-UJI tool using the metadata of the RO present in the ro-crate-metadata file (that it is not analyzed by F-UJI). |
| checks | Yes | \<Check\> | It represents a collection of tests run for each principle. |
| score | Yes | \<Score\> | It represents the partial scores of a component/resource |

### Check

Over a component, a set of tests are run to test each FAIR principle.

The following output is an example of a check element. There is a check element for each principle analyzed.

```json
{

  "principle\_id": "F1.2",

  "category\_id": "Findable",

  "title": "Data is assigned a persistent identifier.",

  "status": "pass",

  "sources": [

  …

  ],

  "score": 1,

  "total\_score": 1

}
```

The fields of the check element are described in the following table (based on F-UJI notation):

| Property | Mandatory | Expected value | Definition |
| --- | --- | --- | --- |
| principle\_id | Yes | String | It is the identifier of the principle. We have followed the F-UJI notation |
| category | Yes | Enumerate(Findable | Accessible | Interoperable | Reusable) | It is the category of the principle |
| title | Yes | String | It is the title of the principle. You can find their description in the section Research Object metadata |
| status | Yes | Enumerate(pass | fail) | The word "pass" represents if the resource passes all the tests associated with this principle, and "fail" if the resource does not achieve the principle. Note that for each principle, we have a battery of tests to assess the fulfillment of the principle.
 |
| source | Yes | [\<Source\>] | It is the score of the assessment. It is the maximum between the scores given by the tools used. |
| score | Yes | Number | It represents the partial scores of a component/resource |
| total\_score | Yes | Number | Is the maximum value of the score. Note that you can pass the test even if you don't have the maximum score (same happens with the F-UJI tool).
 |

### Source

Tests and scores obtained by the tests depend on the nature of the component. This nature determines the tool used to make the assessment.

The following output is an example of the sources element:

```json
{

  "source": "F-UJI",

  "id": "F-UJI",

  "total\_passed\_tests": 0,

  "total\_tests\_run": 2,

  "explanation": [

    "FAIL: Identifier follows a defined persistent identifier syntax",

    "FAIL: Persistent identifier is resolvable"

  ],

  "assessment": "fail",

  "score": 0,

  "total\_score": 1

  },

  {

  "source": "ro-crate",

  "score": 1,

  "total\_tests\_run": 2,

  "total\_passed\_tests": 2,

  "total\_score": 1,

  "assessment": "pass",

  "explanations": [

    "PASS: Identifier follows a defined persistent identifier syntax",

    "PASS: Persistent identifier is resolvable"

  ]

}
```

The fields of the check element are the following:

| Property | Mandatory | Expected value | Definition |
| --- | --- | --- | --- |
| source | Yes | String | It is the tool used for the assessment. |
| id | Yes | Enumerate(ro-crate-metaF-UJI | somef | foops) | It is an id of the tool used |
| total\_passed\_tests | Yes | Number | It is the number of tests passed in this principle. Note that for each principle, there is a battery of tests to analyze different aspects of the principle.
 |
| total\_test\_run | Yes | Number | It is the number of tests run.
 |
| explanations | Yes | String | It is a collection of messages with the results of each test. |
| assessment | Yes | Enumerate (pass | fail) | It represents if the resource passes the tests or not for this principle. This result is given by the tool used. |
| score | Yes | Number | It is the score of the assessment. It is the maximum between the scores given by the tools used. |
| total\_score | Yes | Number | Is the maximum value of the score. Note that you can pass the test even if you don't have the maximum score (same happens with the F-UJI tool).
 |

You can see in this example that we use two tools for the assessment. This is because the tools we use analyze the resource using the identifier, but not analyze the information provided by the ro-crate-metadata file, that is the file used by our service. For that, we have the internal tool ro-crate-metadata to analyze the information of this file, and complement the analysis done by the external tool. As you can see in the example, this tool is executed when the test of the tool fails.

### Score

Each component has a summary of the scores obtained by category. You can find an example here:

```json

"score": {

  "Findable": {

  "tests\_passed": 4,

  "total\_tests": 5,

  "score": 3.5,

  "total\_score": 7

  },

  "Accessible": {

  "tests\_passed": 2,

  "total\_tests": 3,

  "score": 1.5,

  "total\_score": 3

  },

  "Interoperable": {

  "tests\_passed": 3,

  "total\_tests": 3,

  "score": 3.0,

  "total\_score": 4

  },

  "Reusable": {

  "tests\_passed": 3,

  "total\_tests": 5,

  "score": 3,

  "total\_score": 10
  }

}
```

Note that when we talk about tests, we don't refer to the simple tests run in each principle, but to the test of the principle as overall (status field). Remember that we consider that each principle has one test, composed of multiple small tests.

You can find the complete JSON output in the following [link](http://fairos.linkeddata.es/api/assessment/360270ea-e056-4be7-b342-aeb48e485a80).

## Principles analyzed by resource - Research Object metadata

| principle\_id | F1 |
| --- | --- |
| category\_id | Findable |
| title | (Meta)data are assigned a persistent identifier |
| description | This check verifies if the RO has a persistent identifier ['w3id.org', 'doi.org', 'purl.org', 'www.w3.org'] |
| total\_passed\_tests |
 |
| total\_tests\_run |
 |
| status | [pass | fail] |
| explanation | The identifier (https://google.es) of the root data entity is not persistent. The identifier should be store in any of this [w3id.org, doi.org, purl.org, www.w3.org] |

| principle\_id | F2 |
| --- | --- |
| category\_id | Findable |
| title | Data are described with rich metadata |
| description | This check verifies if the the following minimum metadata ['author', 'license', 'description'] are present in the ro-crate |
| total\_passed\_tests |
 |
| total\_tests\_run |
 |
| status | [pass | fail] |
| explanation | Missing the following metadata: [license | author | description] |

| principle\_id | F3 |
| --- | --- |
| category\_id | Findable |
| title | Metadata clearly and explicitly include the identifier of the data they describe. |
| description | This check verifies that the hasPart elements exists and are describe in the ro |
| total\_passed\_tests |
 |
| total\_tests\_run |
 |
| status | [pass | fail] |
| explanation | This IRI could not be found: XXXXXXXX is described but has not been found locally |

| principle\_id | R1.1 |
| --- | --- |
| category\_id | Reusable |
| title | (Meta)data are released with a clear and accessible data usage license. |
| description | This check verifies whether the RO has a licence. It also checks that there is a licence in RO parts. |
| total\_passed\_tests |
 |
| total\_tests\_run |
 |
| status | [pass | fail] |
| explanation | These entities have no licence: [XXXX,YYYY;ZZZZ] |

| principle\_id | R1.2 |
| --- | --- |
| category\_id | Reusable |
| title | (Meta)data are associated with detailed provenance. |
| description | This check verifies that all elements of the RO have the following fields: ['author', 'datePublished', 'citation']. |
| total\_passed\_tests |
 |
| total\_tests\_run |
 |
| status | [pass | fail] |
| explanation | [XXXX does not have author, datePublished, citation] (list of elements) |

**DATA**

| principle\_id | F1.1 |
| --- | --- |
| category\_id | Findable |
| title | Data is assigned a globally unique identifier. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Identifier is resolvable and follows a defined unique identifier syntax (IRI, URL),- Identifier is not resolvable but follows an UUID or HASH type syntax" |

| principle\_id | F1.2 |
| --- | --- |
| category\_id | Findable |
| title | Data is assigned a globally unique identifier. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Identifier follows a defined persistent identifier syntax- Persistent identifier is resolvable |

| principle\_id | F2 |
| --- | --- |
| category\_id | Findable |
| title | Data are described with rich metadata |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Missing the following metadata: XXXX,YYYY
 |

| principle\_id | F2.1 |
| --- | --- |
| category\_id | Findable |
| title | Metadata includes descriptive core elements (creator, title, data identifier, publisher, publication date, summary and keywords) to support data findability. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Metadata has been made available via common web methods,- Metadata is embedded in the landing page XHTML/HTML code,- Metadata is accessible through content negotiation,- Metadata is accessible via typed links,- Metadata is accessible via signposting links,- Core data citation metadata is available,- Core descriptive metadata is available |

| principle\_id | F3.2 |
| --- | --- |
| category\_id | Findable |
| title | Metadata includes the identifier of the data it describes. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Metadata contains data content related information (file name, size, type),- Metadata contains a PID or URL which indicates the location of the downloadable data content
 |

| principle\_id | F3.2 |
| --- | --- |
| category\_id | Findable |
| title | Metadata is offered in such a way that it can be retrieved programmatically. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Metadata is registered in major research data registries (DataCite),- Metadata is given in a way major search engines can ingest it for their catalogues (JSON-LD, Dublin Core, RDFa), |

| principle\_id | A1.1 |
| --- | --- |
| category\_id | Accesible |
| title | Metadata contains access level and access conditions of the data. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Information about access restrictions or rights can be identified in metadata,- fail: Data access information is machine readable,- Data access information is indicated by (not machine readable) standard terms |

| principle\_id | A1.2 |
| --- | --- |
| category\_id | Accesible |
| title | Metadata is accessible through a standardized communication protocol. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | - Landing page link is based on standardized web communication protocols. |

| principle\_id | A1.3 |
| --- | --- |
| category\_id | Accesible |
| title | Data is accessible through a standardized communication protocol. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | - Metadata includes a resolvable link to data based on standardized web communication protocols. |

| principle\_id | I1.1 |
| --- | --- |
| category\_id | Interoperable |
| title | Metadata is represented using a formal knowledge representation language. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Parsable, structured metadata (JSON-LD, RDFa) is embedded in the landing page XHTML/HTML code,- Parsable, graph data (RDF, JSON-LD) is accessible through content negotiation, typed links or sparql endpoint |

| principle\_id | I1.2 |
| --- | --- |
| category\_id | Interoperable |
| title | Metadata uses semantic resources |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Vocabulary namespace URIs can be identified in metadata,- Namespaces of known semantic resources can be identified in metadata |

| principle\_id | I1.3 |
| --- | --- |
| category\_id | Interoperable |
| title | Metadata includes links between the data and its related entities. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Related resources are explicitly mentioned in metadata,- Related resources are indicated by machine readable links or identifiers |

| principle\_id | R1.1 |
| --- | --- |
| category\_id | Reusable |
| title | Metadata specifies the content of the data. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 8 |
| status | [pass | fail] |
| explanation | - Minimal information about available data content is given in metadata",- Resource type (e.g. dataset) is given in metadata",- Information about data content (e.g. links) is given in metadata",- Verifiable data descriptors (file info, measured variables or observation types) are specified in metadata",- File size and type information are specified in metadata",- Measured variables or observation types are specified in metadata",- Data content matches file type and size specified in metadata",- Data content matches measured variables or observation types specified in metadata |

| principle\_id | R1.1.1 |
| --- | --- |
| category\_id | Reusable |
| title | Metadata includes license information under which data can be reused. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - Licence information is given in an appropriate metadata element,- Recognized licence is valid and registered at SPDX |

| principle\_id | R1.2.1 |
| --- | --- |
| category\_id | Reusable |
| title | Metadata includes provenance information about data creation or generation. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | - - Metadata contains elements which hold provenance information and can be mapped to PROV- Metadata contains provenance information using formal provenance ontologies (PROV-O) |

| principle\_id | R1.3.1 |
| --- | --- |
| category\_id | Reusable |
| title | Metadata follows a standard recommended by the target research community of the data. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 3 |
| status | [pass | fail] |
| explanation | - Community specific metadata standard is detected using namespaces or schemas found in provided metadata or metadata services outputs,- Community specific metadata standard is listed in the re3data record of the responsible repository,- Multidisciplinary but community endorsed metadata (RDA Metadata Standards Catalog) standard is listed in the re3data record or detected by namespace" |

| principle\_id | R1.3.2 |
| --- | --- |
| category\_id | Reusable |
| title | Data is available in a file format recommended by the target research community. |
| description | - |
| total\_passed\_tests |
 |
| total\_tests\_run | 4 |
| status | [pass | fail] |
| explanation | - The format of a data file given in the metadata is listed in the long term file formats, open file formats or scientific file formats controlled list,- The format of the data file is an open format",- The format of the data file is a long term format",- The format of the data file is a scientific format" |

**ONTOLOGY**

| principle\_id | F1 |
| --- | --- |
| category\_id | Findable |
| title | Persistent URL |
| description | This check verifies if the ontology has a persistent URL (w3id, purl, DOI, or a W3C URL). |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | Ontology URI is persistent |

| principle\_id | F1 |
| --- | --- |
| category\_id | Findable |
| title | Ontology URI is resolvable |
| description | Ontology URL is resolvable in application/rdf+xml. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | This check verifies if the ontology URI found within the ontology document is resolvable. |

| principle\_id | F1 |
| --- | --- |
| category\_id | Findable |
| title | Version IRI. |
| description | This check verifies if there is an id for this ontology version, and whether the id is unique (i.e., different from the ontology URI). |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | Version IRI defined, IRI is different from ontology URI. |

| principle\_id | F1 |
| --- | --- |
| category\_id | Findable |
| title | Version IRI resolves. |
| description | This check verifies if the version IRI resolves. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | Version IRI resolves. |

| principle\_id | F1 |
| --- | --- |
| category\_id | Findable |
| title | Consistent ontology IDs. |
| description | This check verifies if the ontology URI is equal to the ontology ID. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | Ontology URI is equal to ontology id. |

| principle\_id | F2 |
| --- | --- |
| category\_id | Findable |
| title | Data are described with rich metadata. |
| description | This check verifies if the the following minimum metadata ['author', 'license', 'description'] are present in the research object. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | Missing the following metadata: author, license. |

| principle\_id | F3 |
| --- | --- |
| category\_id | Findable |
| title | Ontology prefix |
| description | This check verifies if an ontology prefix is available. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | Prefix declaration found in the ontology: exo. |

| principle\_id | F4 |
| --- | --- |
| category\_id | Findable |
| title | Prefix is in registry. |
| description | This check verifies if the ontology prefix can be found in prefix.cc or LOV registries. This check also verifies if the prefix resolves to the same namespaceprefix found in the ontology. |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | Prefix declaration found with correct namespace (in prefic.cc). |

| principle\_id | F4 |
| --- | --- |
| category\_id | Findable |
| title | Ontology in metadata registry. |
| description | Ontology not found in a public registry. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | This check verifies if the ontology can be found in a public registry (LOV). |

| principle\_id | A1 |
| --- | --- |
| category\_id | Accesible |
| title | Open protocol. |
| description | The ontology uses an open protocol. |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | This check verifies if the ontology uses an open protocol (HTTP or HTTPS). |

| principle\_id | A1 |
| --- | --- |
| category\_id | Accesible |
| title | Content negotiation for RDF and HTML. |
| description | This check verifies of the ontology URI is published following the right content negotiation for RDF and HTML. |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | Ontology available in: HTML, RDF. |

| principle\_id | A1.1 |
| --- | --- |
| category\_id | Accesible |
| title | Open protocol. |
| description | This check verifies if the ontology uses an open protocol (HTTP or HTTPS). |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | The ontology uses an open protocol. |

| principle\_id | A2 |
| --- | --- |
| category\_id | Accesible |
| title | Metadata are accessible, even when ontology is not. |
| description | Metadata are accessible even when the ontology is no longer available. Since the metadata is usually included in the ontology, this check verifies whether the ontology is registered in a public metadata registry (LOV). |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | Ontology not found in a public registry. |

| principle\_id | I2 |
| --- | --- |
| category\_id | Interoperable |
| title | Vocabulary reuse (metadata). |
| description | Ontology reuses existing vocabularies for declaring metadata.. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | This check verifies if the ontology reuses other vocabularies for declaring metadata terms. |

| principle\_id | I2 |
| --- | --- |
| category\_id | Interoperable |
| title | Vocabulary reuse. |
| description | This check verifies if the ontology imports/extends other vocabularies (besides RDF, OWL and RDFS). |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | Could not find any imported/reused vocabularies. |

| principle\_id | R1 |
| --- | --- |
| category\_id | Reusable |
| title | Documentation: labels. |
| description | This check verifies the extent to which all ontology terms have labels (rdfs:label in OWL vocabularies, skos:prefLabel in SKOS vocabularies). |
| total\_passed\_tests |
 |
| total\_tests\_run | 7 |
| status | [pass | fail] |
| explanation | Labels found for all ontology terms. |

| principle\_id | R1 |
| --- | --- |
| category\_id | Reusable |
| title | Documentation: definitions. |
| description | This check verifies whether all ontology terms have descriptions (rdfs:comment in OWL vocabularies, skos:definition in SKOS vocabularies). |
| total\_passed\_tests |
 |
| total\_tests\_run | 7 |
| status | [pass | fail] |
| explanation | Descriptions found for all ontology terms. |

| principle\_id | R1 |
| --- | --- |
| category\_id | Reusable |
| title | HTML availability. |
| description | This check verifies if the ontology has an HTML documentation. |
| total\_passed\_tests |
 |
| total\_tests\_run | 5 |
| status | [pass | fail] |
| explanation | Ontology available in HTML. |

| principle\_id | R1 |
| --- | --- |
| category\_id | Reusable |
| title | Optional metadata. |
| description | This check verifies if the following optional metadata [doi, previous version,publisher, logo, backwards compatibility, status, modified, source, issued date] are present in the ontology. |
| total\_passed\_tests |
 |
| total\_tests\_run | 9 |
| status | [pass | fail] |
| explanation | The following metadata was not found: doi, publisher, logo, status, modified, source, issued. |

| principle\_id | R1.1 |
| --- | --- |
| category\_id | Reusable |
| title | License availability. |
| description | A license was found http://creativecommons.org/licenses/by/2.0/. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | This check verifies if a license associated with the ontology. |

| principle\_id | R1.1 |
| --- | --- |
| category\_id | Reusable |
| title | License is resolvable. |
| description | This check verifies if the ontology license is resolvable. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | License could be resolved. |

| principle\_id | R1.1 |
| --- | --- |
| category\_id | Reusable |
| title | (Meta)data are released with a clear and accessible data usage license. |
| description | This check verifies whether the element in the research object has a licence. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | This element has no licence. |

| principle\_id | R1.2 |
| --- | --- |
| category\_id | Reusable |
| title | Basic provenance metadata. |
| description | This check verifies if basic provenance is available for the ontology: [author, creation date]. |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | All basic provenance metadata found!Warning: We could not find the following optional provenance metadata: contributor. Please consider adding them if appropriate. |

| principle\_id | R1.2 |
| --- | --- |
| category\_id | Reusable |
| title | (Meta)data are associated with detailed provenance. |
| description | This check verifies that the element in the reserch object has the following fields: ['author', 'datePublished', 'citation']. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | This element has no :author, datePublished, citation. |

| principle\_id | R1.2 |
| --- | --- |
| category\_id | Reusable |
| title | Detailed provenance metadata. |
| description | This check verifies if detailed provenance information is available for the ontology: [issued date, publisher]. |
| total\_passed\_tests |
 |
| total\_tests\_run | 2 |
| status | [pass | fail] |
| explanation | The following provenance information was not found: issued, publisher. Warning: We could not find the following provenance metadata: contributor Please consider adding them (if appropriate). |

**SOFTWARE**

| principle\_id | F1 |
| --- | --- |
| category\_id | Findable |
| title | Software is assigned a globally unique and persistent identifier. |
| description | This test checks if there is at least one DOI for this Software. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | A Digital Object Identifier (DOI) is assigned to the Software. |

| principle\_id | F1.1 |
| --- | --- |
| category\_id | Findable |
| title | Different versions of the same software must be assigned distinct identifiers. |
| description | This test checks if every version has different and uniques identifiers. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | Each version has a different identifier. |

| principle\_id | F2 |
| --- | --- |
| category\_id | Findable |
| title | Software is described with rich metadata. |
| description | This check verifies if the following minimum metadata [title, description, license, installation instructions, requirements, creator, creationDate] are present. |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | The software contains the following metadata [title, description, license, installation instructions, requirements, creator, creationDate]. |

| principle\_id | R1.1 |
| --- | --- |
| category\_id | Reusable |
| title | (Meta)data are released with a clear and accessible data usage license |
| description | This test verifies whether the element in the research object has a license |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | This element have no licence |

| principle\_id | R1.2 |
| --- | --- |
| category\_id | Reusable |
| title | (Meta)data are associated with detailed provenance |
| description | This test verifies that the element in the research object has the following fields: ['author', 'datePublished', 'citation'] |
| total\_passed\_tests |
 |
| total\_tests\_run | 1 |
| status | [pass | fail] |
| explanation | This element has no :author, datePublished or citation |
