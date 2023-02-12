import React from 'react';
import './percentSetting.css';

export default function PercentSetting(props) {
    const handleChange = (e) => {
        let newSetting = props.setting;
        newSetting.value = [e.target.value];
        props.handleSettingChange(newSetting);

    };
    return (
        <div id='Percent-setting' className={"Setting ui segment input padded column"}>
            <h5 className={'ui header'}>
                {props.setting.displayName}
            </h5>
            <div className='ui input'>
                <input type='number' 
                id={props.setting.outputName} 
                value={props.setting.value} 
                onChange={handleChange}
                step={props.setting.step}/>
                <label htmlFor={props.setting.outputName}>
                    <i className="percent icon"></i>
                </label>
            </div>
        </div>
    );
};