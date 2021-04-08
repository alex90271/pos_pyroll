import React from 'react';
import './PathSetting.css';

export default function PathSetting(props) {
    return(
        <div className="Setting" id='Path-setting'>
            <h3>
                {props.setting.displayName}
            </h3>
        </div>
    );
};