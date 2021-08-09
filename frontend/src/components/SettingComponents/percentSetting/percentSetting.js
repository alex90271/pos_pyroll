import React from 'react';
import './percentSetting.css';

export default function PercentSetting(props) {
    const handleChange = (e) => {
        let newSetting = props.setting;
        newSetting.value = [e.target.value];
        props.handleSettingChange(newSetting);

    };
    return (
        <div className="Setting" id='Percent-setting'>
            <h3>
                {props.setting.displayName}
            </h3>
            <input type='number' 
            id={props.setting.outputName} 
            value={props.setting.value} 
            onChange={handleChange}/>
            <label htmlFor={props.setting.outputName}>%</label>
        </div>
    );
};