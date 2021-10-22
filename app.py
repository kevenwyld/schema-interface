from flask import Flask, render_template, request
import json

app = Flask(__name__, static_folder='./static', template_folder='./static')
json_string = ''

nodes = {}
edges = []

# TODO: be able to read quizlet 7 schema.json
# TODO: read the first schema (Disease Outbreak with Hierarchy)

# KSF version 0.8
schema_key_dict = {
    'root': ['@id', 'super', 'name', 'description', 'comment'],
    'step': ['@id', '@type', 'aka', 'reference', 'provenance'],
    'participant': ['@id', 'name', 'aka', 'role', 'entityTypes', 'comment', 'reference'],
    'value': ['valueId', 'value', 'entityTypes', 'mediaType', 'confidence', 'provenance'],
    'slot': ['@id', 'refvar', 'roleName', 'super', 'aka']
}

# SDF version 1.2
# schema_key_dict = {
#     'root': ['@id', 'name', 'description', 'comment', '@type', 'repeatable'],
#     'participant': ['@id', 'roleName', 'entity'],
#     'child': ['child', 'comment', 'outlinks', 'outlink_gate', 'optional']
# }

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

def create_edge(_id, _source, _target, _label='', _edge_type=''):
    """Creates an edge.

    Parameters:
    _id (str): source_target
    _source (str): source node @id
    _target (str): target node @id
    _label (str): label shown in graph
    _edge_type (str): type of edge, influences shape on graph
    
    """
    return {
        'data': {
            'id': _id,
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
                        e_id = f"{before_id}_{after_id}"
                        e.append(create_edge(e_id, before_id, after_id, label, 'step_step'))
            else:
                if before_id in node_set and order['after'] in node_set:
                    e_id = f"{before_id}_{order['after']}"
                    e.append(create_edge(e_id, before_id, order['after'], label, 'step_step'))
    else:
        if isinstance(order['after'], list):
            for after_id in order['after']:
                if order['before'] in node_set and after_id in node_set:
                    e_id = f"{order['before']}_{after_id}"
                    e.append(create_edge(e_id, order['before'], after_id, label, 'step_step'))
        else:
            if order['before'] in node_set and order['after'] in node_set:
                e_id = f"{order['before']}_{order['after']}"
                e.append(create_edge(e_id, order['before'], order['after'], label, 'step_step'))
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
    """Creates lists of nodes and edges, through references and
    relations.

    Parameters:
    schema (dict): contains information on all nodes and edges in a schema.

    Returns:
    nodes (dict): dictionary of nodes
    edges (list): list of edges 

    """
    nodes = {}
    edges = []
    steps_to_connect = []
    
    nodes['root'] = extend_node(create_node('root', 'Start', 'root', 'round-rectangle'), schema)

    # what is slots referring to? I don't see it on the graph
    if 'slots' in schema and isinstance(schema['slots'], list):
        for slot in schema['slots']:
            if 'refvar' in slot:
                nodes[slot['refvar']] = extend_node(create_node(slot['refvar'], slot['roleName'], 'slot', 'ellipse'), slot)

    # nodes and edges to show on graph, ie. children and participants
    for step in schema['steps']:
        _label = step['name'].split('/')[-1].replace('_', ' ')
        nodes[step['@id']] = extend_node(create_node(step['@id'], _label, 'step', 'ellipse'), step)

        steps_to_connect.append(step['@id'])

        if 'participants' in step and isinstance(step['participants'], list):
            for participant in step['participants']:
                nodes[participant['@id']] = extend_node(create_node(participant['@id'], participant['name'], 'participant', 'round-pentagon'), participant)
                
                e_id = f"{step['@id']}_{participant['@id']}"
                edges.append(create_edge(e_id, step['@id'], participant['@id'], _edge_type='step_participant'))

                # coreference 
                if 'refvar' in participant and participant['refvar'] and participant['refvar'] in nodes:
                    e_id = f"{participant['refvar']}_{participant['@id']}"
                    edges.append(create_edge(e_id, participant['refvar'], participant['@id'], _edge_type='slot_participant'))

                # not in the sample schema
                if 'values' in participant and isinstance(participant['values'], list):
                    for value in participant['values']:
                        nodes[value['name']] = create_node(value['name'], value['name'], 'value', 'round-diamond')

                        e_id = f"{participant['@id']}_{value['name']}"
                        edges.append(create_edge(e_id, participant['@id'], value['name'], _edge_type='participant_value'))
    
    # order of events ie. outlinks
    for order in schema['order']:
        if 'overlaps' in order:
            pass
            # for node_id in order['overlaps']:
            #     node = get_node_by_id(node_id)
            #     node['classes'] = ' overlapped'
        # not in sample schema
        elif 'contained' in order and 'container' in order:
            if nodes[order['contained']]:
                nodes[order['contained']]['data']['parent'] = order['container']
        # prev node and next node
        elif 'before' in order and 'after' in order:
            e = []
            
            # not in sample schema
            if 'flags' in order:
                e = handle_flags(order['flags'], order, nodes)
            else:
                e = handle_precondition(order, nodes, 'Before')
                for entry in e:
                    entry['classes'] = 'optional-before'
            edges.extend(e)
            
            # remove connected nodes from the step list
            if isinstance(order['after'], list):
                for step_id in order['after']:
                    if step_id in steps_to_connect:
                        steps_to_connect.remove(step_id)
            else:
                if order['after'] in steps_to_connect:
                        steps_to_connect.remove(order['after'])

    # labels edges with relations; creates new participant nodes if the node does not exist
    if 'entityRelations' in schema and isinstance(schema['entityRelations'], list):
        for entityRelation in schema['entityRelations']:
            subject = entityRelation['relationSubject']
            for relation in entityRelation['relations']:
                predicate = relation['relationPredicate'].split('/')[-1]
                rel_object = relation['relationObject'] if isinstance(relation['relationObject'], list) else [relation['relationObject']]
                for obj in rel_object:
                    edges.append(create_edge(f"{subject}_{obj}", subject, obj, predicate, 'participant_participant'))
                    if obj not in nodes:
                        nodes[obj] = create_node(obj, obj, 'participant', 'round-pentagon')

    # connects root edge to the first Start node
    for step in steps_to_connect:
        e = create_edge(f"root_{step}", 'root', step, _edge_type='root_step')
        e['classes'] = 'root-edge'
        edges.append(e)
        
    return nodes, edges

def get_connected_nodes(selected_node):
    n = []
    e = []
    id_set = set()
    
    if selected_node == 'root':
        n.append(nodes[selected_node])
        for key, node in nodes.items():
            if node['data']['_type'] == 'step':
                n.append(node)
        for edge in edges:
            if edge['data']['_edge_type'] == 'step_step' or edge['data']['_edge_type'] == 'root_step':
                e.append(edge)
    else:
        for edge in edges:
            if (edge['data']['source'] == selected_node or edge['data']['target'] == selected_node) and edge not in e:
                e.append(edge)
                node = nodes[edge['data']['target']]
                if node['data']['_type'] == 'participant':
                    n.append(node)
                    id_set.add(node['data']['id'])
        for edge in edges:
            if edge['data']['source'] in id_set or edge['data']['target'] in id_set:
                if edge not in e:
                    e.append(edge)
                    source_node = nodes[edge['data']['source']]
                    target_node = nodes[edge['data']['target']]
                    if source_node not in n:
                        n.append(source_node)
                    if target_node not in n:
                        n.append(target_node)
            
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
    schemaJson = json.loads(schema_string)['schemas']
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

@app.route('/node', methods=['GET'])
def get_subtree():
    if not (bool(nodes) and bool(edges)):
        return 'Parsing error! Upload the file again.', 400
    node_id = request.args.get('ID')
    subtree = get_connected_nodes(node_id)
    return json.dumps(subtree)

@app.route('/reload', methods=['POST'])
def reload_schema():
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