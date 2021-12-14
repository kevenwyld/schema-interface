import React from "react";
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import isEmpty from 'lodash/isEmpty';

function SideBar (props) {
    /*
    Handles sidebar that shows general information about a node
    selected via right-click.
    */
    let i = 0;
    const excluded_ids = ['id', '_label', '_type', '_shape'];
    
    return (
        <div className={props.className}>
            {isEmpty(props.data) ? '' : 
                <List disablePadding dense>
                    {Object.entries(props.data).map(([key, val]) => {
                        if (!excluded_ids.includes(key)) {
                            val = val.toString()

                            return (
                                <div key={++i}>
                                    <ListItem key={key}>
                                        <ListItemText style={{'overflowWrap': 'anywhere'}}>
                                            <div>{key.toUpperCase()}:</div>
                                            <div>{val}</div>
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

export default SideBar;