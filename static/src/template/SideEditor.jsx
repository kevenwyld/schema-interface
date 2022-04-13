import React, { useEffect, useState } from "react";
import {
    List,
    ListItem,
    ListItemText,
    Divider
} from '@mui/material/';
import { isBoolean, isEmpty } from "lodash";
import Editable from './Editable';
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import FormControlLabel from "@mui/material/FormControlLabel";
import Box from "@mui/material/Box";

// TODO: give q-node label an external URL to wikidata
// TODO: validation checks on some fields
function SideEditor(props) {
    /*
    Handles sidebar that shows general information about a node
    selected via right-click.

    When an inline field is left-clicked to be edited, the
    original data is frozen in 'edit'.
    The JSON is only changed if the field is changed out of
    focus and the field is different from the frozen data. 
    */
    const initData = {
        propData: props.data,
    };

    const [data, setData] = useState(initData);
    const [edit, setEdit] = useState('');

    useEffect(() => {
        setData({ ...data, propData: props.data })
    }, [props.data]);

    const handleChange = (e) => {
        if(edit === ''){
            setEdit(data.propData[e.target.id]);
        }
        data.propData[e.target.id] = e.target.value;
        setData({ ...data });
        if(edit === e.target.value){
            setEdit('');
        }
    };

    const handleEdit = (e) => {
        const node_data = {
            id: data.propData['id'],
            key: e.target.id,
            value: e.target.value
        };
        if(e.target.id === '@id'){
            data.propData['id'] = e.target.value;
            setData({ ...data });
            console.log(data.propData['id']);
        }
        if(edit !== ''){
            props.sideEditorCallback(node_data);
        }
    };

    const handleSwitch = (e) => {
        const val = data.propData[e.target.name];
        const new_val = e.target.checked;
        if(val !== new_val){
            const node_data = {
                id: data.propData['id'],
                key: e.target.name,
                value: new_val
            };
            props.sideEditorCallback(node_data);
        }
    };

    let i = 0;
    const excluded_ids = ['id', '_label', '_type', '_shape', 'outlinks', '_edge_type', 'child'];

    return (
        <div className={props.className}>
            {isEmpty(data.propData)
                ? ''
                : <Box
                    component="form"
                    sx={{
                    '& > :not(style)': { m: 1, width: '25ch' },
                    }}
                    noValidate
                    autoComplete="off"
                >
                    {Object.entries(data.propData).sort().map(([key, val]) => {
                        if (!excluded_ids.includes(key)) {
                            val = isBoolean(val) ? val : val.toString()
                            return (
                                <div key={++i}>
                                    {isBoolean(val)
                                        ? <FormControlLabel
                                            label={key}
                                            labelPlacement="start"
                                            control={<Switch name={key} checked={val} />}
                                            onChange={e => handleSwitch(e)}
                                        />
                                        : <TextField
                                            id={key}
                                            label={key}
                                            value={val}
                                            multiline={true}
                                            onChange={e => handleChange(e)}
                                            onBlur={e => handleEdit(e)}
                                        />
                                    }
                                </div>
                            )
                        }
                    })}
                </Box>
            }
        </div>
    );
}

export default SideEditor;