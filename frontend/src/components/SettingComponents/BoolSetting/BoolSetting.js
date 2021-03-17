import React, { useState } from 'react';
import './BoolSetting.css';

export default function BoolSetting(props) {
    return(
        <div className="Setting">
            <h3>
                {props.setting.displayName}
            </h3>
        </div>
    );
};