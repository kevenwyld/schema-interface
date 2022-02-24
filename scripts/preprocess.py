import json

# Not sure if this still works
file = 'path/to/file.json'
with open(f'{file}', encoding='utf8') as f:
    schema_string = f.read()
schemaJson = json.loads(schema_string)
schema = schemaJson['events']

# extract event dictionary
eventDict = {}
for scheme in schema:
    eventDict[scheme['@id']] = scheme['name']

# change children_gate and add comments to children
for scheme in schema:
    if 'children' in scheme:
        for child in scheme['children']:
            # check name
            if 'Events' not in child['child']:
                event_id = list(eventDict.keys())[list(eventDict.values()).index(child['child'])]
                child['comment'] = child['child']
                child['child'] = event_id
            else:
                child['comment'] = eventDict[child['child']]

schemaJson['events'] = schema
jsonObject = json.dumps(schemaJson, indent = 4)
with open(f"{file[:-5]}_processed.json", "w") as outf:
    outf.write(jsonObject)
