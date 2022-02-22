from tkinter import E
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

# SDF version 1.4
schema_key_dict = {
    'event': ['@id', 'name', 'comment', 'description', 'aka', 'qnode', 'qlabel', 'minDuration', 'maxDuration', 'goal', 'ta1explanation', 'importance', 'children_gate'],
    'child': ['child', 'comment', 'optional', 'importance', 'outlinks', 'outlink_gate'],
    'privateData': ['@type', 'template', 'repeatable', 'importance'],
    'entity': ['name', '@id', 'qnode', 'qlabel', 'centrality']
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
            '_label': f"\n\u2060{_label}\n\u2060",
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
    
    Returns:
    node (dict): extended node
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

def get_entities(entities):
    """Creates lists of entity nodes through the schema entity ontology.
    
    Parameters:
    entities (dict): information on all entities in a schema

    Returns:
    nodes (dict): entity nodes in the schema
    """
    nodes = {}
    for entity in entities:
        _label = entity['name']
        entity_id = entity['@id']
        nodes[entity_id] = extend_node(create_node(entity_id, _label, 'entity'), entity)

    return nodes

def get_relations(relations):
    """Creates edges between entities through the schema relation ontology.

    Parameters:
    nodes (dict): nodes in the schema
    relations (dict): information on all relations in a schema

    Returns:
    nodes (dict): nodes in the schema
    edges (list): edges in the schema
    """
    edges = []
    # 'relation': ['name', 'relationSubject', 'relationPredicate', 'relationObject', '@id']
    for relation in relations:
        edge = create_edge(_source = relation['relationSubject'],
                           _target = relation['relationObject'],
                           _label = relation['name'],
                           _edge_type = 'relation')
        edge['data']['@id'] = relation['@id']
        edge['data']['predicate'] = relation['relationPredicate']
        edges.append(edge)

    return edges

def handle_containers(nodes, edges, containers):
    """Connects incoming and outgoing edges and removes all unvisualized nodes and edges.
    
    Parameters:
    nodes (dict): nodes in the schema
    edges (list): edges in the schema
    containers (list): list of containers to be processed and removed

    Returns:
    nodes (dict): nodes in the schema
    edges (list): edges in the schema
    """
    edges_to_remove = []
    for container in containers:
        in_edges = []
        out_edges = []
        parent_edge = ['', '']
        # find all edges connected to the container
        for edge in edges:
            if edge['data']['target'] == container:
                if edge['data']['_edge_type'] == 'step_child':
                    parent_edge[0] = edge['data']['source']
                else:
                    in_edges.append(edge['data']['source'])
                edges_to_remove.append(edge)
            if edge['data']['source'] == container:
                if edge['data']['_edge_type'] == 'step_child':
                    parent_edge[1] = edge['data']['target']
                out_edges.append(edge['data']['target'])
                edges_to_remove.append(edge)
        # add hierarchical edge
        if parent_edge[0] != '' and parent_edge[1] != '':
            edges.append(create_edge(parent_edge[0], parent_edge[1], _edge_type='step_child'))
        # attach other edges
        if len(in_edges) == 1:
            for out in out_edges:
                edges.append(create_edge(in_edges[0], out, _edge_type='child_outlink'))
        else:
            for edge in in_edges:
                edges.append(create_edge(edge, out_edges[0], _edge_type='child_outlink'))
        nodes.pop(container)

    for index in edges_to_remove:
        edges.remove(index)
    
    return nodes, edges

def get_nodes_and_edges(schemaJson):
    """Creates lists of nodes and edges through the schema event ontology.

    Parameters:
    schemaJson (dict): entire schema in json form

    Returns:
    nodes (dict): nodes in the schema
    edges (list): edges in the schema
    """
    
    # get entities and relations
    nodes = get_entities(schemaJson['entities'])
    edges = get_relations(schemaJson['relations'])

    # get events and attach entities to them
    containers_to_remove = []
    events = schemaJson['events']
    for event in events:
        # create event node
        # if node already exists, add information
        _label = event['name'].split('/')[-1].replace('_', ' ').replace('-', ' ')
        event_id = event['@id']
        if event_id in nodes:
            nodes[event_id]['data']['_type'] = 'event'
            nodes[event_id]['data']['_label'] = _label
            nodes[event_id] = extend_node(nodes[event_id], event)
            if 'children' not in event:
                nodes[event_id]['data']['_type'] = 'child'
            elif 'outlinks' in nodes[event_id]['data']['name'].lower():
                nodes[event_id]['data']['_type'] = 'container'
                containers_to_remove.append(event_id)
            else:
                nodes[event_id]['data']['_type'] = 'parent'
                nodes[event_id]['data']['_shape'] = 'diamond'
        else:
            nodes[event_id] = extend_node(create_node(event_id, _label, 'event', 'diamond'), event)
            nodes[event_id]['data']['_type'] = 'parent'

        # not hierarchical node, change node type to a leaf
        if 'children' not in event:
            nodes[event_id]['data']['_type'] = 'child'
            nodes[event_id]['data']['_shape'] = 'ellipse'
        # handle repeatable
        if 'repeatable' in nodes[event_id]['data'] and nodes[event_id]['data']['repeatable']:
            edges.append(create_edge(event_id, event_id, _edge_type='child_outlink'))

        # link participants to entities
        if 'participants' in event:
            for participant in event['participants']:
                _label = participant['roleName']
                entity_id = participant['entity']
                edge = create_edge(event_id, entity_id, _label, _edge_type='step_participant')
                edge['data']['@id'] = participant['@id']
                edges.append(edge)

        # children
        if 'children' in event:
            gate = 'or'
            if nodes[event_id]['data']['children_gate'] == 'xor':
                gate = 'xor'
                xor_id = f'{event_id}xor'
                nodes[xor_id] = create_node(xor_id, 'XOR', 'gate', 'rectangle')
            elif nodes[event_id]['data']['children_gate'] == 'and':
                gate = 'and'
            
            for child in event['children']:
                # add child information or create new node
                child_id = child['child']
                if child_id in nodes:
                    prev_type = nodes[child_id]['data']['_type']
                    nodes[child_id]['data']['_type'] = 'child'
                    nodes[child_id] = extend_node(nodes[child_id], child)
                    nodes[child_id]['data']['_type'] = prev_type
                else:                    
                    nodes[child_id] = extend_node(create_node(child_id, child['comment'], 'child', 'ellipse'), child)

                # handle xor gate or just add edges
                if gate == 'xor':
                    edges.append(create_edge(xor_id, child_id, _edge_type='child_outlink'))
                    edges.append(create_edge(event_id, xor_id, _edge_type='step_child'))
                else:
                    edges.append(create_edge(event_id, child_id, _edge_type='child_outlink' if gate == 'and' else 'step_child'))
            
                # add outlinks
                if len(child['outlinks']):
                    for outlink in child['outlinks']:
                        if outlink not in nodes:
                            _label = outlink.split('/')[-1].replace('_', '')
                            nodes[outlink] = create_node(outlink, _label, 'child', 'ellipse')
                        edges.append(create_edge(child_id, outlink, _edge_type='child_outlink'))

    nodes, edges = handle_containers(nodes, edges, containers_to_remove)

    # find root node(s)
    parentless_edge = {}
    for edge in edges:
        if edge['data']['source'] not in parentless_edge:
            if nodes[edge['data']['source']]['data']['_type'] == 'entity':
                parentless_edge[edge['data']['source']] = False
            else:
                parentless_edge[edge['data']['source']] = True
        parentless_edge[edge['data']['target']] = False
    roots = [edge for edge in parentless_edge if parentless_edge[edge] == True]
    for root in roots:
        nodes[root]['data']['_type'] = 'root'

    # TODO: entities and relations
    # Zoey wants an entity-first view, so all entities are shown, with groups of events around them in clusters
        # Q: are we able to make a tab on the viewer itself to switch between views?
        
    return nodes, edges

def update_json(values):
    """Updates JSON with values.

    Parameters:
    values (dict): contains node id, key, and value to change key to.
    e.g. {id: node_id, key: name, value: Test}

    Returns:
    schemaJson (dict): new JSON 
    """
    print("values received")
    print(values)

    global schemaJson
    new_json = schemaJson
    node_id = values['id']
    node_type = False
    key = values['key']
    if key in ['source', 'target']:
        node_type = 'edge'
    new_value = values['value']
    if not node_type:
        node_type = node_id.split('/')[0].split(':')[-1].lower()
    array_to_modify = False
    isRoot = node_id == schema_name

    # TODO how to edit relations and participants through the sidebar?

    # entities or relations
    if node_type in ['entities', 'relations']:
        for entity in new_json[node_type]:
            if entity['@id'] == node_id:
                entity[key] = new_value
    else:
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
            if node_type == 'participants':
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
                    if array_to_modify == 'id' and len(child['outlinks']) > 0:
                        for i in range(len(child['outlinks'])):
                            if child['outlinks'][i] == node_id:
                                child['outlinks'][i] = new_value
                                print(child)


    schemaJson = new_json
    return schemaJson

def get_connected_nodes(selected_node):
    """Constructs graph to be visualized by the viewer.

    Parameters:
    selected_node (str): name of node that serves as the topmost node.

    Returns:
    str: name of root node
    dict: list of nodes and list of edges
    
    """
    n = []
    e = []
    id_set = set()
    
    if selected_node == 'root':
        for _, node in nodes.items():
            if node['data']['_type'] == 'root':
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
            # skip entities
            if selected_node == 'root' and node['data']['_type'] == 'entity':
                continue
            e.append(edge)
            n.append(nodes[edge['data']['target']])
            id_set.add(nodes[edge['data']['target']]['data']['id'])
    
    # causal edges between children
    for id in id_set:
        for edge in edges:
            if edge['data']['source'] == id:
                if edge['data']['_edge_type'] == 'child_outlink':
                    # check if node was created previously
                    if edge['data']['target'] not in id_set:
                        n.append(nodes[edge['data']['target']])
                    e.append(edge)
                if edge['data']['target'] in id_set and edge['data']['_edge_type'] == 'relation':
                    e.append(edge)

    return root_node['data']['name'], {'nodes': n, 'edges': e}

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
    global schema_name
    schemaJson = json.loads(schema_string)
    nodes, edges = get_nodes_and_edges(schemaJson)
    schema_name, parsed_schema = get_connected_nodes('root')
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
        _, subtree = get_connected_nodes(node_id)
        return json.dumps(subtree)
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
    global schema_name
    schemaJson = json.loads(schema_string)
    nodes, edges = get_nodes_and_edges(schemaJson)
    schema_name, parsed_schema = get_connected_nodes('root')
    return json.dumps({
        'parsedSchema': parsed_schema,
        'name': schema_name,
        'schemaJson': schemaJson
    })
