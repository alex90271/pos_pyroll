import React from 'react';
import './PathSetting.css';

export default function PathSetting(props) {
    return(
        <div className="Setting" id='Path-setting' class='ui label column'>
            <h3>
                {props.setting.displayName}
            </h3>
        </div>
    );
};