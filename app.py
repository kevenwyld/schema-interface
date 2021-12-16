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

# SDF version 1.3
schema_key_dict = {
    'root': ['@id', 'name', 'comment', 'description', 'aka', 'qnode', 'qlabel', 'minDuration',
             'maxDuration', 'goal', 'ta1explanation', 'importance', 'children_gate'],
             # TODO: handle xor children_gates
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
    if 'privateData' in obj.keys():
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
    first_run = True
    
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

        if first_run:
            first_run = False
        else:
            # not root node, change node type
            nodes[scheme_id]['data']['_type'] = 'parent'
            nodes[scheme_id]['data']['_shape'] = 'diamond'
        # not hierarchical node, change node shape
        if 'children' not in scheme:
            nodes[scheme_id]['data']['_type'] = 'child'
            nodes[scheme_id]['data']['_shape'] = 'ellipse'
        # handle repeatable
        if nodes[scheme_id]['data']['repeatable']:
            edges.append(create_edge(scheme_id, scheme_id, _edge_type='child_outlink'))

        # participants
        if 'participants' in scheme:
            for participant in scheme['participants']:
                _label = participant['roleName'].split('/')[-1].replace('_', '')
                nodes[participant['@id']] = extend_node(create_node(participant['@id'], _label, 'participant', 'square'), participant)
                
                edges.append(create_edge(scheme_id, participant['@id'], _edge_type='step_participant'))

        # children
        if 'children' in scheme:
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
                edges.append(create_edge(scheme_id, child_id, _edge_type='step_child'))
            
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
            for edge in edges:
                if 'searched' in edge['data'] and edge['data']['searched']:
                    continue
                if edge['data']['target'] == container:
                    source_id = edge['data']['source']
                    nodes[source_id]['data']['children_gate'] = nodes[container]['data']['children_gate']
                    edges_to_remove.append(edge)
                    edge['data']['searched'] = True
                if edge['data']['source'] == container:
                    edges.append(create_edge(source_id, edge['data']['target'], _edge_type='step_child'))
                    edges_to_remove.append(edge)
                    edge['data']['searched'] = True

        for index in edges_to_remove:
            edges.remove(index)

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
    file = request.files['file']
    schema_string = file.read().decode("utf-8")
    schemaJson = json.loads(schema_string)['events']
    schema = schemaJson
    global nodes
    global edges
    nodes, edges = get_nodes_and_edges(schema)
    schema_name = schema[0]['name']
    parsed_schema = get_connected_nodes('root')
    return json.dumps({
        'parsedSchema': parsed_schema,
        'name': schema_name,
        'schemaJson': schemaJson
    })

@app.route('/node', methods=['GET'])
def get_subtree():
    """Gets subtree of the selected node."""
    if not (bool(nodes) and bool(edges)):
        return 'Parsing error! Upload the file again.', 400
    node_id = request.args.get('ID')
    subtree = get_connected_nodes(node_id)
    return json.dumps(subtree)

@app.route('/reload', methods=['POST'])
def reload_schema():
    """Reloads schema; does the same thing as upload."""
    schema_string = request.data.decode("utf-8")
    schemaJson = json.loads(schema_string)
    schema = schemaJson
    global nodes
    global edges
    nodes, edges = get_nodes_and_edges(schema)
    schema_name = schema[0]['name']
    parsed_schema = get_connected_nodes('root')
    return json.dumps({
        'parsedSchema': parsed_schema,
        'name': schema_name,
        'schemaJson': schemaJson
    })