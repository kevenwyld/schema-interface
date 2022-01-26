import React, {Component} from 'react';

import JSONEditor from 'jsoneditor';
import 'jsoneditor/dist/jsoneditor.min.css';

export default class JSONEdit extends Component {
    constructor(props){
        super(props);

        this.handleEvent = this.handleEvent.bind(this);
    }

    // sends JSON back to Viewer when field is out of focus
    handleEvent(node, event){
        if (event.type === 'blur'){
            this.props.parentCallback(this.jsoneditor.get());
        }
    }

    componentDidMount () {
        const options = {
            mode: 'tree',
            enableTransform: false,
            onEvent: this.handleEvent,
            templates: [
                {
                    text: 'Event',
                    title: 'Insert an Event Node',
                    field: '',
                    value: {
                        '@id': 'resin:Events/10000/resin:Events_',
                        'name': 'Event Name',
                        'comment': 'description',
                        'qnode': 'Q1234567',
                        'qlabel': 'qnode',
                        'participants': [],
                        'minDuration': '',
                        'maxDuration': '',
                        'description': 'description',
                        'goal': '',
                        'ta1explanation': '',
                        'children': [],
                        'children_gate': 'or',
                        'privateData': {
                            '@type': '',
                            'template': '',
                            'repeatable': false
                        }
                    }
                },
                {
                    text: 'Participant',
                    title: 'Insert Participant',
                    field: '',
                    value: {
                        '@id': 'resin:Participants/20000/kairos:Primitives_Events_Disaster.Diseaseoutbreak.Unspecified:1_entity',
                        'roleName': 'consult_XPO',
                        'entity': 'resin:Entities/00001/'
                    }
                },
                {
                    text: 'Child',
                    title: 'Insert Child',
                    field: '',
                    value: {
                        'child': 'resin:Events/10023/Steps_kairos',
                        'comment': 'name',
                        'optional': false,
                        'importance': 1,
                        'outlinks': [
                            'outlink',
                            'outlink',
                            'outlink'
                        ]
                    }
                }
            ]
        };

        this.jsoneditor = new JSONEditor(this.container, options);
        this.jsoneditor.set(this.props.schemaJson);
    }

    componentWillUnmount () {
        if (this.jsoneditor) {
        this.jsoneditor.destroy();
        }
    }

    componentDidUpdate() {
        this.jsoneditor.update(this.props.schemaJson);
    }

    render() {
        return (
            <div id="schema-json" className="jsoneditor-react-container" ref={elem => this.container = elem} />
        );
    }
}