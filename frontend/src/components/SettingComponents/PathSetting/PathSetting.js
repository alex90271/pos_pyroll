import React, { useState } from 'react';
import './PathSetting.css';

export default function PathSetting(props) {
    return(
        <div className="Setting">
            <h3>
                {props.setting.displayName}
            </h3>
        </div>
    );
};