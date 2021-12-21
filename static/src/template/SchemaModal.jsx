import React, { Component } from 'react';
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Input, Label, Form, FormGroup } from 'reactstrap';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import axios from 'axios';
import AddCircleIcon from '@material-ui/icons/AddCircle';
// import LineStyleIcon from '@material-ui/icons/LineStyle';
// import PersonIcon from '@material-ui/icons/Person';
// import ChildCareIcon from '@material-ui/icons/ChildCare';

/* Shows a pop-up window to create and edit JSON data. */
// TODO: add submitted data to json
class SchemaModal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modal: false,
      valid: false,
      id: "",
      name: "",
      comment: "",
      description: "",
      aka: "",
      qnode: "",
      qlabel: "",
      minDuration: "",
      maxDuration: "",
      goal: "",
      ta1explanation: "",
      importance: "1.0",
      children_gate: "OR",
      repeatable: false
    }
    this.toggle = this.toggle.bind(this);
    this.onChangeHandler = this.onChangeHandler.bind(this);
    this.validate = this.validate.bind(this);
    this.onClickHandler = this.onClickHandler.bind(this);
  }

  toggle() {
    this.setState({
      modal: !this.state.modal,
      id: "",
      name: "",
      comment: "",
      description: "",
      aka: "",
      qnode: "",
      qlabel: "",
      minDuration: "",
      maxDuration: "",
      goal: "",
      ta1explanation: "",
      importance: "1.0",
      children_gate: "OR"
    })
  }

  validate() {
    /*
    Checks whether required text fields are completed
    and are the right format.
    */
    const err = [];
    
    // id, name, ta1explanation, importance
    if (this.state.id.length === 0){
      err.push("@ID cannot be blank.\n");
    }
    if (this.state.name.length === 0){
      err.push("Name cannot be blank.\n");
    }
    if (this.state.ta1explanation.length === 0){
      err.push("TA1 explanation cannot be blank.\n");
    }
    if (this.state.importance > 1 || this.state.importance < 0){
      err.push("Importance must be a number between 0 and 1.\n");
    }
    if (this.state.qnode.length !== 0){
      var isValidQNode = false;
      if(/Q\d/.test(this.state.qnode)){
        isValidQNode = true;
      }

      if (!isValidQNode){
        err.push("Invalid QNode.\n")
      }
    }
    // show errors
    for (var z = 0; z < err.length; z++) { 
      toast.error(err[z]);
    }
    return err.length === 0;
  }

  onChangeHandler(event) {
    // Set state of inputs.
    if (event.target.name === "repeatable"){
      event.target.value = !event.target.value
    }
    this.setState({
      [event.target.name]: event.target.value
    });
  }

  onClickHandler() {
    /*
    Validates fields and handles add button.
    Shows success or failure.
    If success, closes the sub window.
    */
    
    validated = this.validate();
    if (validated){
      // const data = new FormData();
      // for (var x = 0; x < this.state.selectedFile.length; x++) {
      //   data.append('file', this.state.selectedFile[x]);
      // }
      // axios.post("/upload", data, {
      //   onUploadProgress: ProgressEvent => {
      //     this.setState({
      //       loaded: (ProgressEvent.loaded / ProgressEvent.total * 100),
      //     })
      //   }
      // })
      //   .then(res => { // then print response status
      //     this.props.parentCallback(res.data)
      //     toast.success('upload success');
      //     setTimeout(this.toggle, 1000);
      //   })
      //   .catch(err => { // then print response status
      //     this.setState({ valid: false });
      //     toast.error('upload fail, check console');
      //   });
      setTimeout(this.toggle, 1000);
    }
  }

  render() {
    /*
    Opens up a sub window when Upload Schema button is pressed,
    where you can upload a file or cancel.
    Checks the validity of the file.
    Upon pressing upload, shows an upload progress bar.
    */
    
    const openModal = () => {
      document.getElementById("btn-modal").blur();
      this.toggle();
    }

    return (
      <div>
        <div style={{'display': 'flex', 'justifyContent': 'center'}}>
          <AddCircleIcon type="button" id="btn-modal" color="primary" onClick={openModal}/>
        </div>
        <Modal isOpen={this.state.modal} toggle={this.toggle} className={this.props.className}>
          <ToastContainer />
          <ModalHeader toggle={this.toggle}>Edit Scheme</ModalHeader>

          <ModalBody>
            <Form>
              <FormGroup>
                <Label>@id *<Input required name="id" className="form-control"
                  type="text" value={this.state.id} onChange={this.onChangeHandler} /></Label>
                <Label>name *<Input required name="name" className="form-control"
                  type="text" value={this.state.name} onChange={this.onChangeHandler} /></Label>
              </FormGroup>
              <FormGroup>
                <Label>comment<Input name="comment" className="form-control"
                  type="text" value={this.state.comment} onChange={this.onChangeHandler} /></Label>
                <Label>description<Input name="description" className="form-control"
                  type="text" value={this.state.description} onChange={this.onChangeHandler} /></Label>
              </FormGroup>
              <FormGroup>
                <Label>aka<Input name="aka" className="form-control"
                  type="text" value={this.state.aka} onChange={this.onChangeHandler} /></Label>
              </FormGroup>
              <FormGroup>
                <Label>qnode<Input name="qnode" className="form-control"
                  type="text" value={this.state.qnode} onChange={this.onChangeHandler} /></Label>
                <Label>qlabel<Input name="qlabel" className="form-control"
                  type="text" value={this.state.qlabel} onChange={this.onChangeHandler} /></Label>
              </FormGroup>
              <FormGroup>
                <Label>minDuration<Input name="minDuration" className="form-control"
                  type="text" value={this.state.minDuration} onChange={this.onChangeHandler} /></Label>
                <Label>maxDuration<Input name="maxDuration" className="form-control"
                  type="text" value={this.state.maxDuration} onChange={this.onChangeHandler} /></Label>
              </FormGroup>
              <FormGroup>
                <Label>ta1explanation *<textarea required name="ta1explanation" className="form-control"
                  value={this.state.ta1explanation} onChange={this.onChangeHandler} /></Label>
              </FormGroup>
              <FormGroup>
                <Label>goal<Input name="goal" className="form-control"
                  type="text" value={this.state.goal} onChange={this.onChangeHandler} /></Label>
                <Label>importance *<Input required name="importance" className="form-control"
                  type="number" value={this.state.importance} onChange={this.onChangeHandler} /></Label>
              </FormGroup>
              <FormGroup>
                <Label>children_gate *
                  <select required name="children_gate" className="form-select" value={this.state.children_gate} onChange={this.onChangeHandler}>
                    <option value="OR">OR</option>
                    <option value="AND">AND</option>
                    <option value="XOR">XOR</option>
                  </select>
                </Label>
              </FormGroup>
              <FormGroup> 
                <Label>repeatable<Input name="repeatable" className="form-check-input"
                  type="checkbox" checked={this.state.repeatable} onChange={this.onChangeHandler} /></Label>
              </FormGroup>
            </Form>
          </ModalBody>

          <ModalFooter>
            <Button color="primary" onClick={this.onClickHandler}>
              Add
            </Button>{' '}
            <Button color="secondary" onClick={this.toggle}>Cancel</Button>
          </ModalFooter>
        </Modal>
      </div>
    );
  }
}

export default SchemaModal;