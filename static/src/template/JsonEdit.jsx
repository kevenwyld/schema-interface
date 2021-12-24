import React, {Component} from 'react';

import axios from 'axios';
import JSONEditor from 'jsoneditor';
import '../../node_modules/jsoneditor/dist/jsoneditor.min.css';

// TODO: icons don't show up
// TODO: edits in editor do not reflect in graph
export default class JSONEdit extends Component {
    componentDidMount () {
        const options = {
        mode: 'tree',
        onChangeJSON: this.props.parentCallback
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
        axios.post("/reload", this.props.schemaJson)
            .then(res => {
                this.parentCallback(res.data);
            })
            .catch(err => {
                console.error('reload fail');
                return false;
            });
    }

    render() {
        return (
            <div className="jsoneditor-react-container" ref={elem => this.container = elem} />
        );
    }
}