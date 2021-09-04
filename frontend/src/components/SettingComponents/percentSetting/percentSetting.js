import React from 'react';
import './percentSetting.css';

export default function PercentSetting(props) {
    const handleChange = (e) => {
        let newSetting = props.setting;
        newSetting.value = [e.target.value];
        props.handleSettingChange(newSetting);

    };
    return (
        <div className="Setting" id='Percent-setting' class='ui label input column'>
            <h3 class='ui header'>
                {props.setting.displayName}
            </h3>
            <input type='number' 
            class='ui label input'
            id={props.setting.outputName} 
            value={props.setting.value} 
            onChange={handleChange}
            step='0.01'/>
            <label htmlFor={props.setting.outputName}>
                <i class="percent icon"></i>
            </label>
        </div>
    );
};