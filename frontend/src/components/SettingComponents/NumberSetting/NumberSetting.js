import React from 'react';
import './NumberSetting.css';

export default function NumberSetting(props) {
    const handleChange = (e) => {
        let newSetting = props.setting;
        newSetting.value = [e.target.value];
        props.handleSettingChange(newSetting);
    }

    return (
        <div className={'Setting ui segment input padded column'} id="Number-setting">
            <h5 className={'ui header'}>
                {props.setting.displayName}
            </h5>
            <input type='number' 
            id={props.setting.outputName} 
            value={props.setting.value} 
            onChange={handleChange}/>
        </div>
    );
}