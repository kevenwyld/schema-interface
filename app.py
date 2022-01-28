from flask import Flask, render_template, request
import json

# ===============================================
# app.py
# ------------
# reads json data to send to viewer
# ===============================================

app = Flask(__name__, static_folder='./static', template_folder='./static')

nodes = {}
edges = []
schemaJson = {}

# SDF version 1.3
schema_key_dict = {
    'root': ['@id', 'name', 'comment', 'description', 'aka', 'qnode', 'qlabel', 'minDuration', 'maxDuration', 'goal', 'ta1explanation', 'importance', 'children_gate'],
    'participant': ['@id', 'roleName', 'entity'],
    'child': ['child', 'comment', 'optional', 'importance', 'outlinks', 'outlink_gate'],
    'privateData': ['@type', 'template', 'repeatable', 'importance']
}

def create_node(_id, _label, _type, _shape=''):
    """Creates a node.

    Parameters:
    _id (str): unique id
    _label (str): label shown in graph
    _type (str): type of node according to schema_key_dict
    _shape (str): shape as visualized in graph
    
    """
    return {
        'data': {
            'id': _id,
            '_label': _label if _label else _id,
            '_type': _type,
            '_shape': _shape
        },
        'classes': ''
    }

def create_edge(_source, _target, _label='', _edge_type=''):
    """Creates an edge whose id is "source_target".

    Parameters:
    _source (str): source node @id
    _target (str): target node @id
    _label (str): label shown in graph
    _edge_type (str): type of edge, influences shape on graph
    
    """
    return {
        'data': {
            'id': f"{_source}_{_target}",
            '_label': _label,
            'source': _source,
            'target': _target,
            '_edge_type': _edge_type
        },
        'classes': ''
    }

def extend_node(node, obj):
    """Adds values to the node according to the node type.

    Parameters:
    node (dict): node to extend
    obj (dict): schema with data on the node
    
    """

    for key in obj.keys():
        if key in schema_key_dict[node['data']['_type']]:
            if key == 'optional' and obj[key]:
                node['classes'] = 'optional'
            else:
                node['data'][key] = obj[key]
    if 'privateData' in obj.keys() and len(obj['privateData']) > 0:
        for key in obj['privateData'].keys():
            if key in schema_key_dict['privateData']:
                node['data'][key] = obj['privateData'][key]
    return node

def get_nodes_and_edges(schema):
    """Creates lists of nodes and edges, through references and relations.

    Parameters:
    schema (dict): contains information on all nodes and edges in a schema.

    Returns:
    nodes (dict): dictionary of nodes
    edges (list): list of edges 

    """
    nodes = {}
    edges = []
    containers = []
    parentless_xor = []
    
    for scheme in schema:
        # create event node
        _label = scheme['name'].split('/')[-1].replace('_', ' ').replace('-', ' ')
        scheme_id = scheme['@id']
        # node already exists
        if scheme_id in nodes:
            # add information
            nodes[scheme_id]['data']['_type'] = 'root'
            nodes[scheme_id]['data']['_label'] = _label
            nodes[scheme_id] = extend_node(nodes[scheme_id], scheme)
            # change type back
            if 'children' not in scheme:
                nodes[scheme_id]['data']['_type'] = 'child'
            elif 'outlinks' in nodes[scheme_id]['data']['name']:
                nodes[scheme_id]['data']['_type'] = 'container'
                containers.append(scheme_id)
            else:
                nodes[scheme_id]['data']['_type'] = 'parent'
                nodes[scheme_id]['data']['_shape'] = 'diamond'
        # new node
        else:
            nodes[scheme_id] = extend_node(create_node(scheme_id, _label, 'root', 'diamond'), scheme)

        if '@type' in nodes[scheme_id]['data']:
            # not root node, change node type
            nodes[scheme_id]['data']['_type'] = 'parent'
            nodes[scheme_id]['data']['_shape'] = 'diamond'
        # not hierarchical node, change node shape
        if 'children' not in scheme:
            nodes[scheme_id]['data']['_type'] = 'child'
            nodes[scheme_id]['data']['_shape'] = 'ellipse'
        # handle repeatable
        if 'repeatable' in nodes[scheme_id]['data'] and nodes[scheme_id]['data']['repeatable']:
            edges.append(create_edge(scheme_id, scheme_id, _edge_type='child_outlink'))

        # participants
        if 'participants' in scheme:
            for participant in scheme['participants']:
                _label = participant['roleName'].split('/')[-1]
                nodes[participant['@id']] = extend_node(create_node(participant['@id'], _label, 'participant', 'square'), participant)
                
                edges.append(create_edge(scheme_id, participant['@id'], _edge_type='step_participant'))

        # children
        if 'children' in scheme:
            gate = 'or'
            if nodes[scheme_id]['data']['children_gate'] == 'xor':
                gate = 'xor'
            elif nodes[scheme_id]['data']['children_gate'] == 'and':
                gate = 'and'
            for child in scheme['children']:
                child_id = child['child']
                # node already exists
                if child_id in nodes:
                    prev_type = nodes[child_id]['data']['_type']
                    nodes[child_id]['data']['_type'] = 'child'
                    nodes[child_id] = extend_node(nodes[child_id], child)
                    nodes[child_id]['data']['_type'] = prev_type
                # new node
                else:                    
                    nodes[child_id] = extend_node(create_node(child_id, child['comment'], 'child', 'ellipse'), child)

                # handle xor gate
                if gate == 'xor':
                    xor_id = f'{scheme_id}xor'
                    nodes[xor_id] = create_node(xor_id, 'XOR', 'gate', 'rectangle')
                    edges.append(create_edge(xor_id, child_id, _edge_type='child_outlink'))
                    if 'Container' in scheme_id:
                        edges.append(create_edge(scheme_id, xor_id, _edge_type='child_outlink'))
                        parentless_xor.append((xor_id, child_id))
                    else:
                        edges.append(create_edge(scheme_id, xor_id, _edge_type='step_child'))

                edges.append(create_edge(scheme_id, child_id, _edge_type='child_outlink' if gate == 'and' else 'step_child'))
            
                # check for outlinks
                if len(child['outlinks']):
                    for outlink in child['outlinks']:
                        if outlink not in nodes:
                            _label = outlink.split('/')[-1].replace('_', '')
                            nodes[outlink] = create_node(outlink, _label, 'child', 'ellipse')
                        edges.append(create_edge(child_id, outlink, _edge_type='child_outlink'))

        # handle containers, ie. connect previous node to all their successors
        edges_to_remove = []
        for container in containers:
            edge_type = False
            source_id = False
            for edge in edges:
                if 'searched' in edge['data'] and edge['data']['searched']:
                    continue
                if edge['data']['target'] == container:
                    source_id = edge['data']['source']
                    edge['data']['searched'] = True
                    edges_to_remove.append(edge)
                if edge['data']['source'] == container:
                    edge_type = edge['data']['_edge_type']
                    edge['data']['searched'] = True
                if source_id and edge_type:
                    edges_to_remove.append(edge)
                    edges.append(create_edge(source_id, edge['data']['target'], _edge_type=edge_type))
                    edge_type = False

        for index in edges_to_remove:
            edges.remove(index)

        # give xor nodes a parent node they belong to
        parent_found = []
        for xor_id, child_id in parentless_xor:
            if xor_id in parent_found:
                continue
            for edge in edges:
                if edge['data']['target'] == child_id and edge['data']['_edge_type'] == 'step_child':
                    edges.append(create_edge(edge['data']['source'], xor_id, _edge_type='step_child'))
                    parent_found.append(xor_id)
                    break

        # === are these two necessary? / what are these for ===
        # TODO: entities
        # TODO: relations

        # if 'entityRelations' in schema and isinstance(schema['entityRelations'], list):
        #     for entityRelation in schema['entityRelations']:
        #         subject = entityRelation['relationSubject']
        #         for relation in entityRelation['relations']:
        #             predicate = relation['relationPredicate'].split('/')[-1]
        #             rel_object = relation['relationObject'] if isinstance(relation['relationObject'], list) else [relation['relationObject']]
        #             for obj in rel_object:
        #                 edges.append(create_edge(f"{subject}_{obj}", subject, obj, predicate, 'participant_participant'))
        #                 if obj not in nodes:
        #                     nodes[obj] = create_node(obj, obj, 'participant', 'round-pentagon')
        
    return nodes, edges

def update_json(values):
    """Updates JSON with values.

    Parameters:
    values (dict): contains node id, key, and value to change key to.
    e.g. {id: node_id, key: name, value: Test}

    Returns:
    schemaJson (dict): new JSON 
    """
    global schemaJson
    new_json = schemaJson
    node_id = values['id']
    key = values['key']
    new_value = values['value']
    node_type = node_id.split('/')[0].split(':')[-1]
    array_to_modify = False
    isRoot = new_json['events'][0]['@id'] == node_id

    # what key is it?
    # special cases
    if key in ['@id', 'child']:
        key = '@id'
        array_to_modify = 'id'
    elif key == 'importance':
        array_to_modify = 'importance'
    elif key == 'name':
        array_to_modify = 'name'
    # look for the key in schema_key_dict
    if not array_to_modify:
        if node_type == 'Participants':
            array_to_modify = 'participant'
        else:
            for keys in schema_key_dict:
                if key in schema_key_dict[keys]:
                    array_to_modify = keys
                    break

    # change schemaJson
    for scheme in new_json['events']:
        # scheme data
        if scheme['@id'] == node_id:
            if array_to_modify in ['root', 'name', 'privateData']:
                if key in schema_key_dict['privateData']:
                    scheme['privateData'][key] = new_value
                    break
                else:
                    scheme[key] = new_value
                    if key != 'name':
                        break
                if isRoot:
                    break    
            elif array_to_modify == 'importance':
                if isRoot:
                    scheme['privateData'][key] = new_value
                    break
            elif array_to_modify == 'id':
                scheme[key] = new_value
                if isRoot:
                    break
        # participant data
        if array_to_modify in ['participant', 'id'] and 'participants' in scheme:
            for participant in scheme['participants']:
                if participant['@id'] == node_id:
                    scheme[key] = new_value
        # children data
        if array_to_modify in ['child', 'id', 'name'] and 'children' in scheme:
            for child in scheme['children']:
                if child['child'] == node_id:
                    if array_to_modify == 'name':
                        child['comment'] = new_value
                    elif array_to_modify == 'id':
                        child['child'] = new_value
                    else:
                        child[key] = new_value

    schemaJson = new_json
    return schemaJson

def get_connected_nodes(selected_node):
    """Constructs graph to be visualized by the viewer.

    Parameters:
    selected_node (str): name of node that serves as the topmost node.

    Returns:
    dict:list of nodes and list of edges
    
    """
    n = []
    e = []
    id_set = set()
    
    if selected_node == 'root':
        for _, node in nodes.items():
            if node['data']['_type'] == selected_node:
                root_node = node
                n.append(node)
                id_set.add(node['data']['id'])
                break
    else:
        root_node = nodes[selected_node]
    
    # node children
    for edge in edges:
        if edge['data']['source'] == root_node['data']['id']:
            node = nodes[edge['data']['target']]
            # skip participant edges
            if selected_node == 'root' and node['data']['_type'] == 'participant':
                continue
            e.append(edge)
            n.append(nodes[edge['data']['target']])
            id_set.add(nodes[edge['data']['target']]['data']['id'])
    
    # causal edges between children
    for id in id_set:
        for edge in edges:
            if edge['data']['source'] == id and edge['data']['_edge_type'] == 'child_outlink':
                # check if node was created previously
                if edge['data']['target'] not in id_set:
                    n.append(nodes[edge['data']['target']])
                e.append(edge)

    return {
        'nodes': n,
        'edges': e
    }

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Uploads JSON and processes it for graph view."""
    file = request.files['file']
    schema_string = file.read().decode("utf-8")
    global schemaJson
    global nodes
    global edges
    schemaJson = json.loads(schema_string)
    schema = schemaJson['events']
    nodes, edges = get_nodes_and_edges(schema)
    schema_name = schema[0]['name']
    parsed_schema = get_connected_nodes('root')
    return json.dumps({
        'parsedSchema': parsed_schema,
        'name': schema_name,
        'schemaJson': schemaJson
    })

@app.route('/node', methods=['GET', 'POST'])
def get_subtree_or_update_node():
    if not (bool(nodes) and bool(edges)):
        return 'Parsing error! Upload the file again.', 400

    if request.method == 'GET':        
        """Gets subtree of the selected node."""
        node_id = request.args.get('ID')
        subtree = get_connected_nodes(node_id)
        return json.dumps(subtree)
    # it won't work and i don't know why
    else:
        """Posts updates to selected node and reloads schema."""
        values = json.loads(request.data.decode("utf-8"))
        new_json = update_json(values)
        return json.dumps(new_json)
        


@app.route('/reload', methods=['POST'])
def reload_schema():
    """Reloads schema; does the same thing as upload."""
    schema_string = request.data.decode("utf-8")
    global schemaJson
    global nodes
    global edges
    schemaJson = json.loads(schema_string)
    schema = schemaJson['events']
    nodes, edges = get_nodes_and_edges(schema)
    schema_name = schema[0]['name']
    parsed_schema = get_connected_nodes('root')
    return json.dumps({
        'parsedSchema': parsed_schema,
        'name': schema_name,
        'schemaJson': schemaJson
    })
