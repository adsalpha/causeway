# Causeway v2 Specification

## Endpoints

To be written.

###### 


## Request Handling

#### Collections

All data received by Causeway is stored in document collections. There are three collections:
1. `jobs` stores processed and encrypted job data in a monolithic job document
2. `users` stores user profiles
3. `requests` logs nonce tokens and raw requests to ensure

Normally Causeway will serve data from the first collection. The third one is only present for the client to check that the server owner did not alter stored data.

#### Helper Class

`CausewayRequest` is a helper class for POST requests. It generates nonce strings and logs the requesting user to make sure that the upcoming request is genuine.

When a POST request is submitted, a `CausewayRequest` object validates the nonce string, the user, and logs the request payload.

## Documents

All document classes must subclass the `Document` abstract base class.

#### Creating New Documents

All documents have a unique `new` constructor.
It calls four hooks:
1. `set_expected`
2. `set_attributes(as_dict, **kwargs)`
3. `validate`
4. `save`

Subclasses of `Document` must define two attributes:
1. `expected_structure` is a list containing string keys that the document submitted by the client should also define.
Nested keys like `{ key1: { child1, child2 }}` check if the incoming payload contains `{ key1: { child1: foo, child2: bar }}`.
The `Document` class defines the `_base_expected_structure` attribute that contains fields common for all documents.
What subclasses set is appended to this attribute.
2. `expected_type` is a string that defines the document type. For all applicable values please see the RDS.

Documents set their OrderedDict implementation in the `set_attributes` method.
Encrypted documents set the parent in the same method.


Documents pass validation before they are added to the database.

The base `Document` class defines four validators:
1. `expected_structure_ok` checks for a programmatic error in setting the `expected_structure` attribute.
2. `incoming_structure_ok` checks the incoming document structure against the expected one.
3. `type_ok` checks the incoming document `type` field against the `expected_type` attribute.
4. `is_duplicate` should only be implemented if the database engine cannot determine by itself if a document is unique.

After having passed all the checks documents are automatically saved.

#### Querying Documents

All documents must override the `from_database` abstract constructor.

Adjacent documents should be queried using their parent document instance i.e. 
bids should only be accessed using `Job.from_database(<id>).get_bid(<id>)`. 
The route class can but should not query job related documents using the
`from_database` constructor. It is only provided as a compatibility feature. 
Parent documents use the `from_parent` constructor to obtain child documents
using their OrderedDict implementation.
