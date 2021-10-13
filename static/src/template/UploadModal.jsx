import React, { Component } from 'react';
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Progress, Input, Label, Form,FormGroup } from 'reactstrap';
import { ToastContainer, toast } from 'react-toastify';

import axios from 'axios';

class UploadModal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modal: false,
      selectedFile: null,
      loaded: 0,
      valid: false
    }
    this.toggle = this.toggle.bind(this);
    this.onChangeHandler = this.onChangeHandler.bind(this);
    this.checkMimeType = this.checkMimeType.bind(this);
    this.maxSelectFile = this.maxSelectFile.bind(this);
    this.checkFileSize = this.checkFileSize.bind(this);
    this.onClickHandler = this.onClickHandler.bind(this);
  }

  toggle() {
    this.setState({
      modal: !this.state.modal,
      valid: false,
      selectedFile: null,
      loaded: 0,
    })
  }

  checkMimeType(event) {
    /*
    Checks whether the selected file has the correct type.
    If not, throws a toast error and discards the file.
    */

    //getting file object
    let files = event.target.files;
    //define message container
    let err = [];
    // list allow mime type
    const types = ['application/ld+json', 'application/json', 'text/plain'];
    // loop access array
    for (var x = 0; x < files.length; x++) {
      // compare file type find doesn't matach
      if (types.every(type => files[x].type !== type)) {
        // create error message and assign to container   
        err[x] = files[x].type + ' is not a supported format\n';
      }
    };
    for (var z = 0; z < err.length; z++) {// if message not same old that mean has error 
      // discard selected file
      toast.error(err[z]);
      event.target.value = null;
    }
    return err.length === 0;
  }

  maxSelectFile(event) {
    /* 
    Warns the user if they try to upload more than one file.
    If so, throws a warning and discards all files.
    */

    let files = event.target.files;
    if (files.length > 1) {
      const msg = 'Only 1 file can be uploaded at a time';
      event.target.value = null;
      toast.warn(msg);
      return false;
    }
    return true;
  }

  checkFileSize(event) {
    /*
    Checks whether file size is too large.
    If so, throws an error and discards the file.
    */

    let files = event.target.files;
    let size = 2000000;
    let err = [];
    for (var x = 0; x < files.length; x++) {
      if (files[x].size > size) {
        err[x] = files[x].name.substring(0, 10) + ' is too large, please pick a smaller file\n';
      }
    };
    for (var z = 0; z < err.length; z++) {// if message not same old that mean has error 
      // discard selected file
      toast.error(err[z]);
      event.target.value = null;
    }
    return err.length === 0;
  }

  onChangeHandler(event) {
    /*
    Checks the file is valid, then changes state.
    */

    var files = event.target.files;
    if (this.maxSelectFile(event) && this.checkMimeType(event) && this.checkFileSize(event)) {
      // if return true allow to setState
      this.setState({
        selectedFile: files,
        loaded: 0,
        valid: true
      });
    } else {
      this.setState({ valid: false });
      setTimeout(toast.dismiss, 4000);
    }
  }

  onClickHandler() {
    /*
    Handles green upload button.
    Shows upload success or failure.
    If success, closes the sub window.
    */
   
    const data = new FormData();
    for (var x = 0; x < this.state.selectedFile.length; x++) {
      data.append('file', this.state.selectedFile[x]);
    }
    axios.post("/upload", data, {
      onUploadProgress: ProgressEvent => {
        this.setState({
          loaded: (ProgressEvent.loaded / ProgressEvent.total * 100),
        })
      }
    })
      .then(res => { // then print response status
        this.props.parentCallback(res.data)
        toast.success('upload success');
        setTimeout(this.toggle, 1000);
      })
      .catch(err => { // then print response status
        toast.error('upload fail');
      });
  }

  render() {
    /*
    Renders the upload schema button. 
    Opens up a sub window where you can upload a file or cancel.
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
          <Button id="btn-modal" color="primary" onClick={openModal}>
            {this.props.buttonLabel}
          </Button>
        </div>
        <Modal isOpen={this.state.modal} toggle={this.toggle} className={this.props.className}>
          <ModalHeader toggle={this.toggle}>Upload Schema</ModalHeader>

          <ModalBody>
            <Form>
              <FormGroup className="files">
                <Label>Upload Your File</Label>
                <Input type="file" className="form-control" style={{height: 'auto'}} onChange={this.onChangeHandler} />
              </FormGroup>

              <FormGroup>
                <ToastContainer closeButton={false} />
                <Progress max="100" color="success" value={this.state.loaded} >{Math.round(this.state.loaded, 2)}%</Progress>
              </FormGroup>
            </Form>
          </ModalBody>

          <ModalFooter>
            <Button disabled={!this.state.valid} color="success" onClick={this.onClickHandler}>
              Upload
            </Button>{' '}
            <Button color="secondary" onClick={this.toggle}>Cancel</Button>
          </ModalFooter>
        </Modal>
      </div>
    );
  }
}

export default UploadModal;