import React, { useState } from 'react';
import './percentSetting.css';

export default function PercentSetting(props) {
    return (
        <div className="Setting">
            <h3>
                {props.setting.displayName}
            </h3>
            <input type='number'/>
        </div>
    );
};