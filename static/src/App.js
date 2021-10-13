import React from "react";
import { Row, Col } from 'reactstrap';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

import Home from "./template/Home";
import Viewer from "./template/Viewer";
import Compare from "./template/Compare";
import logo from './public/logo.png'

import './App.scss'

export default function App() {
  return (
    <Router>
      <div className="App">
        <Row className="Header">
          <Col md="2" id="logo">
            <img src={'/static'+ logo} alt="Curate" />
          </Col>
          <Col md="4" id="title" className="align-self-center">
            <div><h1>CURATE</h1></div>
            <div><h4 >Schema Curation interface</h4></div>
          </Col>
          <Col md="6" className="align-self-center">
            <Row>
              <Col md="3" className="nav-items">
                <Link to="/" color="white">Home</Link>
              </Col>
              <Col md="3" className="nav-items">
                <Link to="/viewer">Viewer</Link>
              </Col>
              <Col md="3" className="nav-items">
                <Link to="/compare">Compare</Link>
              </Col>
              <Col md="3" className="nav-items">
                <a target="_blank" href="https://github.com/cu-clear/schema-interface">
                  Github
                  </a>
              </Col>
            </Row>
          </Col>
        </Row>

        <Switch>
          <Route path="/viewer">
            <Viewer />
          </Route>
          <Route path="/compare">
            <Compare />
          </Route>
          <Route path="/">
            <Home />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}