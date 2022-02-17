import React, { useEffect, useState } from "react";
import {
    List,
    ListItem,
    ListItemText,
    Divider
} from '@mui/material/';
import isEmpty from 'lodash/isEmpty';

import Editable from './Editable';

// TODO: give q-node label an external URL to wikidata
// TODO: is it possible to order sidebar info in a specific way?
// BUG changing child doesn't seem to actually change @id
// BUG sidebar no longer updates D:
function SideEditor (props) {
    /*
    Handles sidebar that shows general information about a node
    selected via right-click.
    */
    const initData = {
        propData: props.data
    };

    const [data, setData] = useState(initData);

    useEffect (() => { 
        setData({ ...data, propData: props.data}) 
    }, [props.data])
    
    const handleUpdate = (e) => {
        data.propData[e.target.name] = e.target.value;
        setData({...data});
    }

    const handleEdit = (e) => {
        const node_data = {
            id: data.propData['id'],
            key: e.target.name,
            value: e.target.value
        };
        if(e.target.value !== data.propData[e.target.name])
            props.sideEditorCallback(node_data);
    }

    let i = 0;
    const excluded_ids = ['id', '_label', '_type', '_shape', 'outlinks'];
    
    return (
        <div className={props.className}>
            {isEmpty(data.propData) ? '' : 
                <List disablePadding dense>
                    {Object.entries(data.propData).map(([key, val]) => {
                        if (!excluded_ids.includes(key)) {
                            val = val.toString()

                            return (
                                <div key={++i}>
                                    <ListItem key={key}>
                                        <ListItemText style={{'overflowWrap': 'anywhere'}}>
                                            <div>{key.toUpperCase()}</div>
                                            <div>
                                            <Editable text={val} placeholder={val} type="input">
                                                <input type="text" name={key} placeholder={isEmpty(val) ? key : val} value={val} onChange={e => handleUpdate(e)} onBlur={e => handleEdit(e)}/>
                                            </Editable>
                                            </div>
                                        </ListItemText>
                                    </ListItem>
                                    <Divider />
                                </div>
                            )
                        }
                    })}
                </List>
            }
        </div>
    );
}

export default SideEditor;