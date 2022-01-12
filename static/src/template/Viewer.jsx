import React, { Component } from 'react';
import isEmpty from 'lodash/isEmpty';

import DownloadIcon from '@material-ui/icons/CloudDownload';

import axios from 'axios';
import UploadModal from './UploadModal';
import Canvas from './Canvas';
import SideBar from './SideBar';
import JsonEdit from './JsonEdit';

/* Viewer page for the schema interface. */
class Viewer extends Component {
    constructor(props) {
        super(props)

        this.state = {
            schemaResponse: '',
            schemaName: '',
            schemaJson: '',
            isOpen: false,
            isUpload: false,
            downloadUrl: '',
            fileName: 'schema.json',

            nodeData: {}
        }

        this.callbackFunction = this.callbackFunction.bind(this);
        this.jsonEditorCallback = this.jsonEditorCallback.bind(this);
        this.sidebarCallback = this.sidebarCallback.bind(this);
        this.download = this.download.bind(this);

    }

    callbackFunction(response) {
        this.setState({ 
            schemaResponse: Object.assign({}, response.parsedSchema),
            schemaName: response.name,
            schemaJson: response.schemaJson,
            isUpload: true
        });
    }

    download(event){
        event.preventDefault();
        const output = JSON.stringify(this.state.schemaJson, null, 4)
        const blob = new Blob([output], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        this.setState({downloadUrl: url},
            () => {
                this.dofileDownload.click();
                URL.revokeObjectURL(url);
                this.setState({downloadUrl: ''})
        })
    }

    jsonEditorCallback(json){
        axios.post("/reload", json)
            .then(res => {
                console.log('reload success')
                this.callbackFunction(res.data);
            })
            .catch(err => {
                console.error('reload fail:', err);
                return false;
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
        let jsonEdit = "";
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

            // graph (cytoscape)
            canvas = <Canvas id="canvas"
                elements={this.state.schemaResponse}
                sidebarCallback={this.sidebarCallback}
                className={canvasClassName}
            />;
            
            jsonEdit = <JsonEdit
                style={{width: 'inherit', height: '75vh'}}
                schemaJson={this.state.schemaJson}
                parentCallback={this.jsonEditorCallback}
            />
        
        } else {
            if (navEle) {
                navEle.classList.remove("shrink");
            }
        }

        return (
            <div id="viewer">
                <div className='container'>
                    <UploadModal buttonLabel="Upload Schema" parentCallback={this.callbackFunction} />
                    <DownloadIcon className="button" type="button" color={this.state.isUpload ? "action" : "disabled"} onClick={this.download}/>
                    <a style={{display: "none"}}
                        download={this.state.fileName}
                        href={this.state.downloadUrl}
                        ref={e=>this.dofileDownload = e}
                    >download it</a>
                </div>
                <div className="row">{schemaHeading}</div>
                <div style={{display: 'inline-flex'}}>
                    <SideBar
                        data={this.state.nodeData}
                        isOpen={this.state.isOpen} 
                        className={sidebarClassName} />
                    {canvas}
                    {jsonEdit}
                </div>
            </div>
        )
    }
}

export default Viewer;