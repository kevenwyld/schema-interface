import json
import getopt, sys


def main(argv):
    h = """
    preprocess.py
    ======================================================================
    Input the JSON file you want to preprocess.
    This script preprocesses a JSON file to make sure it can be imported
    into SCI 2.0.

    Currently the script fixes children gates to 'or' to show
    hierarchy, and adds missing values to child lists to prevent errors
    from SCI 2.0.

    *note: if it does not read your file, try putting your file path in
    double quotes, e.g. "path\\to\\file" on Windows.
    ======================================================================
    -h      help
    -i      input file
    """
    # obtain arguments
    input_file = ''
    try:
        opts, _ = getopt.getopt(argv, "hi:", ["help", "inputfile="])
    except getopt.GetoptError:
        print('error')
        print(h)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(h)
            sys.exit()
        if opt in ("-i", "--inputfile"):
            input_file = arg

    # exit with help
    if input_file == '':
        print(h)
        sys.exit(2)

    # check input file is a json
    if 'json' not in input_file[-5:]:
        print("ERROR: please input a JSON file.")
        print(h)
        sys.exit(2)

    file = input_file[:-5]
    with open(f'{file}.json', encoding='utf8') as f:
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
            scheme['children_gate'] = 'or'

            for child in scheme['children']:
                # check name
                if 'Events' not in child['child']:
                    event_id = list(eventDict.keys())[list(eventDict.values()).index(child['child'])]
                    child['comment'] = child['child']
                    child['child'] = event_id
                else:
                    child['comment'] = eventDict[child['child']]
                
                if 'optional' not in child:
                    child['optional'] = False

    schemaJson['events'] = schema
    jsonObject = json.dumps(schemaJson, indent = 4)
    with open(f"{file}_processed.json", "w") as outf:
        outf.write(jsonObject)
    print(f"New file is available at {file}_processed.json.")

if __name__ == "__main__":
    main(sys.argv[1:])