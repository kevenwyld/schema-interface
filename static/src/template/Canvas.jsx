import React from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import klay from 'cytoscape-klay';

import axios from 'axios';
import isNull from 'lodash/isNull';
import equal from 'fast-deep-equal';
import RefreshIcon from '@material-ui/icons/Refresh';

import Background from '../public/canvas_bg.png';
import CyStyle from '../public/cy-style.json';
import { get } from 'lodash';

cytoscape.use(klay)

// TODO : update subtree to be able to click nodes in subtrees

class Canvas extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            canvasElements: CytoscapeComponent.normalizeElements(this.props.elements),
            currentSubtree: null
        }

        this.showSidebar = this.showSidebar.bind(this);
        this.showSubTree = this.showSubTree.bind(this);
        this.removeSubTree = this.removeSubTree.bind(this);
        this.runLayout = this.runLayout.bind(this);
        this.reloadCanvas = this.reloadCanvas.bind(this);
    }

    showSidebar(data) {
        this.props.sidebarCallback(data);
    }

    showSubTree(node) {
        axios.get('/node', {
            params: {
                ID: node.id
              }
            })
            .then(res => {
                if (!isNull(this.state.currentSubtree) && this.state.currentSubtree !== res.data) {
                    this.removeSubTree(this.state.currentSubtree);
                }
                this.setState({currentSubtree: res.data});
                this.cy.add(res.data);
                this.runLayout();
            })
            .catch(err => {
                console.error(err);
            })
    }

    removeSubTree(currentSubtree) {
        this.reloadCanvas();
        // const nodes = currentSubtree.nodes;
        // for (let i = 0; i < nodes.length; i++) {
        //     if (nodes[i].data._type == 'child' || nodes[i].data.id === 'root') {
        //         let el = this.cy.getElementById(nodes[i].data.id);
        //         this.cy.remove(el);
        //     }
        // }
        // this.runLayout();
        // this.setState({currentSubtree: null});
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
            currentSubtree: null
        });
        this.cy.elements().remove(); 
        this.cy.add( this.state.canvasElements );
        this.runLayout();
    }

    componentDidMount() {
        console.log('mounted')
        this.cy.ready(() => {
            // left-click 
            this.cy.on('tap', event => {
                var eventTarget = event.target;
                // click background, reset canvas
                if (eventTarget === this.cy) {
                    this.reloadCanvas();
                // click node, show subtree
                } else if (eventTarget.isNode()) {
                    let node = eventTarget.data();
                    this.showSubTree(node);
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
                this.props.sidebarCallback(event.target.data());
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
                    maxZoom={4} minZoom={0.5}
                />
                <div style={{'width': '0', height: '3vh'}}>
                    <RefreshIcon type='button' color="action" fontSize='large' onClick={this.reloadCanvas}/>
                </div>
            </div>
        );
    }
}

export default Canvas;