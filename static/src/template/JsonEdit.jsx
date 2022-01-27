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
                        '@id': 'Events/10000/Event',
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
                        '@id': 'Participants/20000/Participant',
                        'roleName': 'consult_XPO',
                        'entity': 'Entities/00001/'
                    }
                },
                {
                    text: 'Child',
                    title: 'Insert Child',
                    field: '',
                    value: {
                        'child': 'Events/10023/Steps_kairos',
                        'comment': 'name',
                        'optional': false,
                        'importance': 1,
                        'outlinks': [
                            'outlink',
                            'outlink',
                            'outlink'
                        ]
                    }
                },
                {
                    text: 'Entity',
                    title: 'Insert Entity',
                    field: '',
                    value: {
                        'child': 'Entities/00023/',
                        'name': 'name',
                        'qnode': 'Q1234567',
                        'qlabel': 'qlabel',
                        'centrality': 1.0
                    }
                },
                {
                    text: 'Relation',
                    title: 'Insert Relation',
                    field: '',
                    value: {
                        'relationSubject': 'Entities/00023/',
                        'relationPredicate': 'Q1234567',
                        'relationObject': 'Entities/00023/',
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