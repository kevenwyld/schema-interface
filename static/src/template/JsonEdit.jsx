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
                    title: 'Insert Event',
                    field: '',
                    value: {
                        '@id': 'Events/10000/Event',
                        'name': 'Event Name',
                        'description': '',
                        'qnode': 'wd:Q1234567',
                        'qlabel': 'qnode name',
                        'participants': [],
                        'ta1explanation': '',
                        'privateData': {
                            '@type': '',
                            'template': '',
                            'repeatable': false
                        }
                    }
                },
                {
                    text: 'Container',
                    title: 'Insert Container',
                    field: '',
                    value: {
                        '@id': 'Events/10000/Event:Container',
                        'name': 'Event outlinks',
                        'comment': 'container node',
                        'children_gate': 'or',
                        'children': [],
                        'privateData': {
                            '@type': 'kairos:Container',
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
                        '@id': 'Participants/20000/Participant',
                        'roleName': 'consult_XPO',
                        'entity': 'Entities/00001/'
                    }
                },
                {
                    text: 'Children',
                    title: 'Insert Children',
                    field: '',
                    value: {
                        'children_gate': 'or',
                        'children': [],
                    }
                },
                {
                    text: 'Child',
                    title: 'Insert Child',
                    field: '',
                    value: {
                        'child': 'Events/10000/Event',
                        'comment': 'name',
                        'optional': false,
                        'importance': 1,
                        'outlinks': []
                    }
                },
                {
                    text: 'Entity',
                    title: 'Insert Entity',
                    field: '',
                    value: {
                        '@id': 'Entities/00000/',
                        'name': 'name',
                        'qnode': 'wd:Q1234567',
                        'qlabel': 'qlabel'
                    }
                },
                {
                    text: 'Relation',
                    title: 'Insert Relation',
                    field: '',
                    value: {
                        'name': '',
                        'relationSubject': 'Entities/00000/',
                        'relationPredicate': 'wd:Q1234567',
                        'relationObject': 'Entities/00000/',
                        '@id': 'Relations/30000/'
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