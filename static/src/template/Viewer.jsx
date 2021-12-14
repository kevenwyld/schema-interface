import React, { Component } from 'react';
import isEmpty from 'lodash/isEmpty';

import UploadModal from './UploadModal';
import Canvas from './Canvas';
import SideBar from './SideBar';
import JsonView from './JsonView';

class Viewer extends Component {
    constructor(props) {
        super(props)

        this.state = {
            schemaResponse: '',
            schemaName: '',
            schemaJson: '',
            isOpen: false,
            nodeData: {}
        }

        this.callbackFunction = this.callbackFunction.bind(this);
        this.sidebarCallback = this.sidebarCallback.bind(this);
    }

    callbackFunction(response) {
        this.setState({ 
            schemaResponse: Object.assign({}, response.parsedSchema),
            schemaName: response.name,
            schemaJson: response.schemaJson 
        });
    }

    sidebarCallback(data) {
        if (isEmpty(data)) {
            this.setState({
                isOpen: false,
                nodeData: data
            });
        } else {
            this.setState({
                isOpen: true,
                nodeData: data
            });
        }
    }

    render() {
        let canvas = "";
        let schemaHeading = "";
        let jsonViewer = "";
        let navEle = "";
        let sidebarClassName = this.state.isOpen ? "sidebar-open" : "sidebar-closed";
        let canvasClassName = this.state.isOpen ? "canvas-shrunk": "canvas-wide";

        // a schema exists
        if (this.state.schemaResponse !== '') {
            // shrink the header to make space for the schema
            navEle = document.getElementsByClassName('Header')[0];
            navEle.classList.add("shrink");
            
            // title of schema
            schemaHeading = <h3 className="schema-name col-md-8" style={{textAlign: 'center'}}>
                                {this.state.schemaName}
                            </h3>;

            // graph (cytoscape) in the middle
            canvas = <Canvas id="canvas"
                elements={this.state.schemaResponse}
                sidebarCallback={this.sidebarCallback}
                className={canvasClassName}
            />;
            
            // json editor on the right
            jsonViewer = <JsonView 
                schemaJson={this.state.schemaJson} 
                parentCallback={this.callbackFunction}
            />;
        
        } else {
            if (navEle) {
                navEle.classList.remove("shrink");
            }
        }

        return (
            <div id="viewer">
                <UploadModal buttonLabel="Upload Schema" parentCallback={this.callbackFunction} />
                <div className="row">{schemaHeading}</div>
                <div style={{display: 'inline-flex'}}>
                    <SideBar
                        data={this.state.nodeData}
                        isOpen={this.state.isOpen} 
                        className={sidebarClassName} />
                    {canvas}
                    {jsonViewer}
                </div>
            </div>
        )
    }
}

export default Viewer;