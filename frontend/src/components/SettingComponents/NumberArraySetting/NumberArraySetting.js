import React, { useState } from 'react';
import './NumberArraySetting.css';

export default function NumberArraySetting(props) {
    return(
        <div className="Setting">
            <h3>
                {props.setting.displayName}
            </h3>
        </div>
    );
};