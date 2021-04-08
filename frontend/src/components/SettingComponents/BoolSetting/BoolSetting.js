import React from 'react';
import './BoolSetting.css';

export default function BoolSetting(props) {
    const handleChange = (e) => {
        let newSetting = props.setting;
        newSetting.value = JSON.parse(e.target.value);
        props.handleSettingChange(newSetting);
    }
    return(
        <div className="Setting" id="Bool-setting">
            <h3>
                {props.setting.displayName}
            </h3>
            <label>
                True
                <input type='radio' 
                id='true' 
                name={props.setting.outputName} 
                value={true} checked={props.setting.value} 
                onChange={handleChange}/>
            </label>
            <br/>
            <label>
                False
                <input type='radio' 
                id='false' name={props.setting.outputName} 
                value={false} checked={!props.setting.value} 
                onChange={handleChange}/>
            </label>
        </div>
    );
};