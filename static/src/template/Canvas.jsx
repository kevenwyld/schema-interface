import React from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import klay from 'cytoscape-klay';
import contextMenus from 'cytoscape-context-menus'
// want to use https://github.com/iVis-at-Bilkent/cytoscape.js-expand-collapse

import axios from 'axios';
import equal from 'fast-deep-equal';
import RefreshIcon from '@material-ui/icons/Refresh';
import OpenIcon from '@material-ui/icons/OpenWith';

import Background from '../public/canvas_bg.png';
import CyStyle from '../public/cy-style.json';
import 'cytoscape-context-menus/cytoscape-context-menus.css';

// TODO: add uncollapse / unselect without complete reload
cytoscape.use(klay);
cytoscape.use(contextMenus);

/* Graph view of the data.
   Includes reload button. */
class Canvas extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            canvasElements: CytoscapeComponent.normalizeElements(this.props.elements),
            hasSubtree: false,
            // static copy of topmost tree
            topTree: null,
            removed: null
        }

        // create topTree
        var treeData = []
        for (var {data:d} of this.state.canvasElements){
            treeData.push(d);
        };
        this.state.topTree = treeData;

        this.showSidebar = this.showSidebar.bind(this);
        this.showSubTree = this.showSubTree.bind(this);
        this.removeSubTree = this.removeSubTree.bind(this);
        this.runLayout = this.runLayout.bind(this);
        this.reloadCanvas = this.reloadCanvas.bind(this);
        this.removeObject = this.removeObject.bind(this);
        this.restore = this.restore.bind(this);
        this.fitCanvas = this.fitCanvas.bind(this);
    }

    showSidebar(data) {
        this.props.sidebarCallback(data);
    }

    showEditor(data) {
        this.props.editorCallback(data);
    }

    showSubTree(node) {
        axios.get('/node', {
            params: {
                ID: node.id
              }
            })
            .then(res => {
                if (this.state.hasSubtree && this.state.topTree.includes(node)) {
                    this.removeSubTree();
                }
                this.setState({hasSubtree: true});
                this.cy.add(res.data);
                this.runLayout();
            })
            .catch(err => {
                console.error(err);
            })
    }

    removeSubTree() {
        this.reloadCanvas();
        this.setState({hasSubtree: false});
    }

    runLayout() {
        let layout = this.cy.makeLayout(Object.assign({}, CyStyle.layout, {
            ready: e => {
                e.cy.center();
            }
        }));
        layout.run();
    }

    reloadCanvas() {
        this.setState({
            canvasElements: CytoscapeComponent.normalizeElements(this.props.elements),
            hasSubtree: false,
            showParticipants: true
        });
        this.cy.elements().remove(); 
        this.cy.add( this.state.canvasElements );
        this.runLayout();
    }

    removeObject(event) {
        this.setState({removed: event.target});
        event.target.remove();
    }

    restore(){
        var res = null;
        if (this.state.removed){
            res = this.state.removed;
            this.setState({removed: null});
            res.restore();
        }
    }

    fitCanvas(){
        this.cy.fit();
    }

    componentDidMount() {
        this.cy.ready(() => {
            // left-click 
            this.cy.on('tap', event => {
                var eventTarget = event.target;
                //click background
                if (eventTarget === this.cy) {
                    // do nothing
                // click node, show subtree
                } else if (eventTarget.isNode()) {
                    let node = eventTarget.data();
                    this.showSubTree(node);
                    this.cy.center(node);
                }
            });

            // right-click
            this.cy.on('cxttap', event => {
                // collapse sidebar
                if (Object.keys(event.target.data()).length === 0) {
                    this.cy.resize();
                    this.runLayout();
                }
                // show information of node
                this.showSidebar(event.target.data());
            })

            // right-click menu
            var contextMenu = this.cy.contextMenus({
                menuItems: [
                    {
                        id: 'remove',
                        content: 'remove',
                        tooltipText: 'remove',
                        selector: 'node, edge',
                        onClickFunction: this.removeObject,
                        hasTrailingDivider: true
                    },
                    {
                        id: 'undo-last-remove',
                        content: 'undo last remove',
                        selector: 'node, edge',
                        disabled: this.state.removed ? true : false,
                        show: true,
                        coreAsWell: true,
                        onClickFunction: this.restore,
                        hasTrailingDivider: true
                    }
                ]
            })
        })
    }

    componentDidUpdate(prevProps) {
        if(!equal(this.props.elements, prevProps.elements)){
            this.reloadCanvas();
        }
    }

    render() {
        const style = {
            width: 'inherit', 
            height: '75vh',
            borderStyle: 'solid',
            backgroundImage: `url(${"/static" + Background})`
        };

        return (
            <div className={this.props.className} style={{width: 'inherit', display: 'inline-flex'}}>
                <CytoscapeComponent
                    elements={this.state.canvasElements}
                    layout={CyStyle.layout}
                    style={style}
                    stylesheet={CyStyle.stylesheet}
                    cy={(cy) => { this.cy = cy }}
                    maxZoom={3} minZoom={0.5}
                />
                <div style={{'width': '15px', height: '3vh'}}>
                    <RefreshIcon type='button' color="action" fontSize='large' onClick={this.reloadCanvas}/>
                    <OpenIcon type='button' color="action" fontSize='large' onClick={this.fitCanvas}/>
                </div>
            </div>
        );
    }
}

export default Canvas;