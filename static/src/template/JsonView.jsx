import React, { Component } from 'react';
import ReactJson from 'react-json-view';

import axios from 'axios';
import some from 'lodash/some';
import isArray from 'lodash/isArray';
import isObject from 'lodash/isObject';

class JsonView extends Component {
    /*
    Handles the Json viewer and editor.
    Allows you to add, edit, and delete nodes.
    */
    constructor(props) {
        super(props);

        this.handleAdd = this.handleAdd.bind(this);
        this.handleDelete = this.handleDelete.bind(this);
        this.handleEdit = this.handleEdit.bind(this);
    }

    handleAdd (e) {
        if (e.new_value == "error") {
            return false;
        } else if (isArray(e.new_value) && some(e.new_value, null)) {
            return true;
        } else if (isObject(e.new_value) && some(Object.values(e.new_value), null)) {
            return true;
        } else {
            axios.post("/reload", e.updated_src)
                .then(res => {
                    this.props.parentCallback(res.data);
                })
                .catch(err => {
                    console.error('reload fail');
                    return false;
                });
            return true;
        }
    }

    handleDelete (e) {
        if (e.new_value !== "error") {
            axios.post("/reload", e.updated_src)
                .then(res => {
                    this.props.parentCallback(res.data);
                })
                .catch(err => {
                    console.error('reload fail');
                    return false;
                });
        } else {
            return false;
        }
    }

    handleEdit (e) {
        if (e.new_value !== "error") {
            axios.post("/reload", e.updated_src)
                .then(res => {
                    this.props.parentCallback(res.data);
                })
                .catch(err => {
                    console.error('reload fail');
                    return false;
                });
        } else {
            return false;
        }
    }

    render () {
        const style = {
            padding: "15px", 
            backgroundColor: "white", 
            fontSize: "14px"
        }
        return (
            <div id="schema-json">
                <ReactJson 
                    name={"schema"}
                    sortKeys
                    style={style}
                    src={this.props.schemaJson}
                    collapsed={2}
                    displayDataTypes={false}
                    displayObjectSize={true}
                    indentWidth={2}
                    onAdd={this.handleAdd}
                    onDelete={this.handleDelete}
                    onEdit={this.handleEdit}
                />
            </div>
        )
    }
}

export default JsonView;