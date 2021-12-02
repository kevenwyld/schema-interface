from flask import Flask, render_template, request
import json

app = Flask(__name__, static_folder='./static', template_folder='./static')
json_string = ''

nodes = {}
edges = []

# TODO: be able to read quizlet 7 schema.json
# TODO: read the first schema of (Disease Outbreak with Hierarchy)
    # TODO: open participant subtree

# SDF version 1.2
schema_key_dict = {
    'root': ['@id', 'name', 'description', 'comment', '@type', 'repeatable'],
    'participant': ['@id', 'roleName', 'entity'],
    'child': ['child', 'comment', 'outlinks', 'outlink_gate', 'optional'],
    'leaf': ['child', 'comment', 'TA1explanation', 'repeatable', 'optional']
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
    return node

def handle_precondition(order, node_set, label='Precondition'):
    """Adds edges between multiple previous and next nodes.
    
    Parameters:
    order (dict): links to "before" and "after" nodes
    node_set (dict): nodes to be linked
    label (str): shows order on graph

    """
    e = []
    if isinstance(order['before'], list):
        for before_id in order['before']:
            if isinstance(order['after'], list):
                for after_id in order['after']:
                    if before_id in node_set and after_id in node_set:
                        e.append(create_edge(before_id, after_id, label, 'step_child'))
            else:
                if before_id in node_set and order['after'] in node_set:
                    e.append(create_edge(before_id, order['after'], label, 'step_child'))
    else:
        if isinstance(order['after'], list):
            for after_id in order['after']:
                if order['before'] in node_set and after_id in node_set:
                    e.append(create_edge(order['before'], after_id, label, 'step_child'))
        else:
            if order['before'] in node_set and order['after'] in node_set:
                e.append(create_edge(order['before'], order['after'], label, 'step_child'))
    return e

def handle_optional(_order, node_set):
    """Calls handle_precondition with thet optional label.
    
    """
    return handle_precondition(_order, node_set, 'Optional')

def handle_flags(_flag, _order, node_set):
    """Calls handle_precondition or handle_optional based on flag.

    Parameters:
    _flag (str): flag raised in order dictionary
    _node_set (dict): set of nodes to be handled
    
    """
    switcher={
        'precondition': handle_precondition,
        'optional': handle_optional
    }
    func = switcher.get(_flag.lower(), lambda *args: None)
    return func(_order, node_set)

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
    
    for scheme in schema:
        # top node
        _label = scheme['name'].split('/')[-1].replace('_', ' ').replace('-', ' ')
        nodes[scheme['@id']] = extend_node(create_node(scheme['@id'], _label, 'root', 'diamond'), scheme)
        # not root node, change node type
        if '@type' in nodes[scheme['@id']]['data']:
            nodes[scheme['@id']]['data']['_type'] = 'parent'
            # not hierarchical node, change node shape
            if 'children' not in scheme:
                nodes[scheme['@id']]['data']['_type'] = 'child'
                nodes[scheme['@id']]['data']['_shape'] = 'ellipse'
        if scheme['repeatable']:
            edges.append(create_edge(scheme['@id'], scheme['@id'], _edge_type='child_outlink'))


        # participants
        if 'participants' in scheme:
            for participant in scheme['participants']:
                _label = participant['roleName'].split('/')[-1].replace('_', '')
                nodes[participant['@id']] = extend_node(create_node(participant['@id'], _label, 'participant', 'square'), participant)
                
                edges.append(create_edge(scheme['@id'], participant['@id'], _edge_type='step_participant'))

        # children
        if 'children' in scheme:
            for child in scheme['children']:
                nodes[child['child']] = extend_node(create_node(child['child'], child['comment'], 'child', 'ellipse'), child)
                edges.append(create_edge(scheme['@id'], child['child'], _edge_type='step_child'))
            
                # check for outlinks
                if len(child['outlinks']):
                    for outlink in child['outlinks']:
                        if outlink not in nodes:
                            _label = outlink.split('/')[-1].replace('_', '')
                            nodes[outlink] = create_node(outlink, _label, 'leaf', 'ellipse')
                        edges.append(create_edge(child['child'], outlink, _edge_type='child_outlink'))


        # TODO: and, xor gate
        # TODO: repeatable edge
        # TODO: optional nodes

        # === are these two necessary? ===
        # TODO: entities

        # TODO: relations
        # if 'relations' in schema and len(schema['relations']):
        #     # generalize, although at the moment UIUC Q7 only has these two predicates
        #     predicates = {'Q19267375':'proximity', 'Q6498684':'ownership'}
        #     for relation in schema['relations']:

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
    for key, node in nodes.items():
        if node['data']['_type'] == selected_node:
            root_node = node
            n.append(node)
            id_set.add(node['data']['id'])
        break
    
    # node children
    for edge in edges:
        if edge['data']['source'] == root_node['data']['id']:
            e.append(edge)
            n.append(nodes[edge['data']['target']])
            id_set.add(nodes[edge['data']['target']]['data']['id'])
    
    # causal edges between children
    for id in id_set:
        if nodes[id]['data']['_type'] == 'participant':
            continue
        else:
            for edge in edges:
                if edge['data']['source'] == id and edge['data']['_edge_type'] == 'child_outlink':
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
    # TODO: extend to all schemas, not just the first one
    schema = schemaJson[:2]
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
# TODO: participants won't show up, why?
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
    schema = schemaJson[0]
    global nodes
    global edges
    nodes, edges = get_nodes_and_edges(schema)
    schema_name = schema['name']
    parsed_schema = get_connected_nodes('root')
    return json.dumps({
        'parsedSchema': parsed_schema,
        'name': schema['name'],
        'schemaJson': schemaJson
    })