import React from 'react';
import './BoolSetting.css';

export default function BoolSetting(props) {
    const handleChange = (e) => {
        let newSetting = props.setting;
        newSetting.value = JSON.parse(e.target.value);
        props.handleSettingChange(newSetting);
    }
    return(
        <div className={'Setting ui segment input padded column'} id="Bool-setting"> 
            <h5 className={'ui header'}>
                {props.setting.displayName}
            </h5>
            <div className={'ui form'}>
                <div className={'field'}>
                    <div className={'ui radio checkbox'}>
                        <input type='radio' 
                        id='true'
                        name={props.setting.outputName} 
                        value={true} checked={props.setting.value} 
                        onChange={handleChange}/>
                        <label>True</label>
                    </div>
                </div>
            </div>
            <br/>
            <div className={'ui form'}>
                <div className={'field'}>
                    <div className={'ui radio checkbox'}>
                        <input type='radio' 
                        id='false'
                        name={props.setting.outputName} 
                        value={false} checked={!props.setting.value} 
                        onChange={handleChange}/>
                        <label>False</label>
                    </div>
                </div>
            </div>
        </div>
    );
};