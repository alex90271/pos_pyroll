import React from 'react';
import './NumberSetting.css';

export default function NumberSetting(props) {
    const handleChange = (e) => {
        let newSetting = props.setting;
        newSetting.value = [e.target.value];
        props.handleSettingChange(newSetting);
    }

    return (
        <div className='Setting' id="Number-setting">
            <h3>
                {props.setting.displayName}
            </h3>
            <input type='number' 
            id={props.setting.outputName} 
            value={props.setting.value} 
            onChange={handleChange}/>
        </div>
    );
}