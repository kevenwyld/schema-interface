import json
import getopt, sys

def NewId(currId, num, idDict = -1):
    oldId = currId.split('/')
    newId = f"{oldId[0]}/{'0'*(5 - len(str(num)))}{num}/{oldId[-1]}"
    if idDict != -1:
        idDict[currId] = newId
    num += 1
    return newId, num, idDict

def main(argv):
    h = """
    reorder.py
    ======================================================================
    Input the JSON file you want to clean up.
    This script reorders Entities, Relations, Events, and Participant IDs.

    For example, if your list of Entities looks like this:
    [ Entities/00001, Entities/00010, Entities/00248 ]

    This script will reorder it so that the list will look like this:
    [ Entities/00000, Entities/00001, Entities/00002 ]
    And resolve all references to the entities in Participant lists.

    *note: if it does not read your file, try putting your file path in
    double quotes, e.g. "path\\to\\file" on Windows.
    ======================================================================
    -h      help
    -i      input file
    
    Optionals:
    -v      verbose output, i.e. prints which step the program is on
    """
    # obtain arguments
    input_file = ''
    v = 0
    try:
        opts, _ = getopt.getopt(argv, "hi:v", ["help", "inputfile=", "verbose"])
    except getopt.GetoptError:
        print(h)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(h)
            sys.exit()
        if opt in ("-i", "--inputfile"):
            input_file = arg
        elif opt in ("-v", "--verbose"):
            v = 1

    # exit with help
    if input_file == '':
        print(h)
        sys.exit(2)

    # check input file is a json
    if 'json' not in input_file[-5:]:
        print("ERROR: please input a JSON file.")
        print(h)
        sys.exit(2)

    # reorder listed files
    file = input_file[:-5]
    if v: print("Reading file...", end='')
    with open(f'{file}.json', encoding='utf8') as f:
        schema_string = f.read()
    schemaJson = json.loads(schema_string)
    if v: print("done.")

    if v: print("Reordering entities...", end='')
    entities = schemaJson['entities']
    numE = 0
    entDict = {}
    for entity in entities:
        newId, numE, entDict = NewId(entity['@id'], numE, entDict)
        entity['@id'] = newId
    if v: print("done.")

    if v: print("Resolving entity references in relations...", end='')
    relations = schemaJson['relations']
    numR = 30000
    for relation in relations:
        relation['relationSubject'] = entDict[relation['relationSubject']]
        relation['relationObject'] = entDict[relation['relationObject']]
        rid = relation['@id'].split('/')
        relation['@id'] = f'{rid[0]}/{numR}/'
        numR += 1
    if v: print("done.")

    if v: print("Reordering events and participants, resolving entity references...", end='')
    schema = schemaJson['events']
    numP = 20000
    numS = 10000
    schemeDict = {}
    for scheme in schema:
        if scheme['@id'] not in schemeDict:
            newId, numS, schemeDict = NewId(scheme['@id'], numS, schemeDict)
            scheme['@id'] = newId
        else:
            scheme['@id'] = schemeDict[scheme['@id']]

        # children
        if 'children' in scheme:
            for child in scheme['children']:
                if child['child'] not in schemeDict:
                    newId, numS, schemeDict = NewId(child['child'], numS, schemeDict)
                    child['child'] = newId
                else:
                    child['child'] = schemeDict[child['child']]
                
                # child outlinks
                if 'outlinks' in child:
                    for i in range(len(child['outlinks'])):
                        if child['outlinks'][i] not in schemeDict:
                            newId, numS, schemeDict = NewId(child['outlinks'][i], numS, schemeDict)
                            child['outlinks'][i] = newId
                        else:
                            child['outlinks'][i] = schemeDict[child['outlinks'][i]]

        # reorder participants and use new entity ID's
        if 'participants' in scheme:
            for participant in scheme['participants']:
                pid = participant['@id'].split('/')
                participant['@id'] = f'{pid[0]}/{numP}/{pid[2]}'
                numP += 1

                participant['entity'] = entDict[participant['entity']]
    if v: print("done.")

    if v: print("Writing...", end='')
    schemaJson['events'] = schema
    schemaJson['entities'] = entities
    schemaJson['relations'] = relations
    jsonObject = json.dumps(schemaJson, indent = 4)
    with open(f"{file}_reordered.json", "w") as outf:
        outf.write(jsonObject)
    if v: print("done.")
    print(f"New file is available at {file}_reordered.json.")

if __name__ == "__main__":
    main(sys.argv[1:])