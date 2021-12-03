# schema-interface

## Introduction

This is a web tool to visualize KAIROS Schema Format generated schemas using Cytoscape.js and React.js. The tool also allows editing of these schemas for curation purpose. Current supported SDF version is **1.2**.

**This project is currently a work in progress and is in alpha testing. Feedbacks and suggestions are welcome.**

## Getting Started

To run the project locally one needs to have following libraries installed:

* npm 6.13.4 (or latest)
* Python 3.7.3 (or latest)
* pip 20.1.1 (or latest)

First run:

* cd path/to/project/schema-interface
* sh first_run.sh
* _If rendering fails_: sh run_local.sh 

Subsequent runs:

* cd path/to/project/schema-interface
* sh run_local.sh

Once the server has started, run the localhost with the port mentioned in the terminal in the browser. The tool will render.

## Libraries

The tool mainly uses 3 resources:

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) : A Python micro web framework used for writing the backend functionality of the tool. Schema extraction and edit handling has been done in Flask.
* [React.js](https://reactjs.org/): A frontend JavaScript library responible for rendering the UI. All the interactions between the visualization and the backend framwork is handled by React.
* [Cytoscape.js](https://js.cytoscape.org/): A data visualization library that uses the extracted schema, provided by React from backend, to provide a graphical structure in a sequential order. CRUD operations on the visualizations is currently being handled by using _**[react-json-view](https://github.com/mac-s-g/react-json-view/blob/master/README.md)**_ library. This library allows updation of the schemas and Cytoscape reloads the graph with added change.

## Usage

Currently the tool has 4 sections, namely Home, Viewer, Compare, Github. Out of the 4, only the viewer has been implemented. It provides following features.

* An **Upload Schema** button that opens a modal to upload file from the local file system.
* A **Canvas** where the schema is represented. The canvas allows one to zoom-in and zoom-out, move one node at a time and move the entire structure. There is a **reload** icon on the top right corner of the canvas that resets the graph to its original position.
* A **JSON viewer** that gives the json view of the schema. This viewer allows editing of the schema which in turn updates the graph. The viewer allows 4 main funtionality.
  * **Copy**: A "Copy-to-Clipboard" icon shows up on every object of the json structure which allows one to copy the entire value. For object, number and string, it copies the value assigned to the property. For arrays, it copies all the entries in the list.
  * **Add**: A "+" icon signifies adding an entry. Within objects, it expects a key and initialize it with "NULL" which can then be edited to the required value. In arrays, it expects a value in the form of an object or a string.
  * **Edit**: Selecting "notepad-with-pen" icon allows editing the value of the respective key. This option is missing in arrays.
  * **Delete**: Clicking on "X" icon will delete that entry in the object. Using it in array will remove the entire object and reduce the length of the list by 1.
  
  For an interactive [demo](https://mac-s-g.github.io/react-json-view/demo/dist/).
* A **SideBar** opens up on the left side of the canvas giving information about the selected node. This window opens only when a node is right-clicked. It gives the details about the nodes like name, id, role, entityTypes, comments, provenance, confidence etc. These information will only be visible if they are mentioned in the schema.
