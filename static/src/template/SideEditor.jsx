import React, { useEffect, useState } from "react";
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import isEmpty from 'lodash/isEmpty';

import Editable from './Editable';

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
        setData({ ...data, propData: props.data }) 
    }, [props.data])
    console.log(data)
    
    const handleUpdate = (e) => {
        console.log('handle update');
        console.log(e.target);
        targetKey = e.target.name;
        data.propData.targetKey = e.target.value; //targetKey undeclared variable
        setData({...data});
    }

    let i = 0;
    const excluded_ids = ['id', '_label', '_type', '_shape'];
    
    return (
        <div className={props.className}>
            {isEmpty(data.propData) ? 'empty' : 
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
                                                <input type="text" name={key} placeholder={val} value={val} onChange={e => handleUpdate(e, key)} />
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