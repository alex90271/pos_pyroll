import React, { useState } from 'react';
import './NumberSetting.css';

export default function NumberSetting(props) {
    return(
        <div className='Setting'>
            <h3>
                {props.setting.displayName}
            </h3>
        </div>
    );
};