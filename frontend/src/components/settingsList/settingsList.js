import React from 'react';
import './settingsList.css';
import PercentSetting from '../SettingComponents/percentSetting/percentSetting';
import NumberSetting from '../SettingComponents/NumberSetting/NumberSetting';
import BoolSetting from '../SettingComponents/BoolSetting/BoolSetting';
import NumberArraySetting from '../SettingComponents/NumberArraySetting/NumberArraySetting';
import PathSetting from '../SettingComponents/PathSetting/PathSetting';

export default function SettingsList(props) {
    let addedSettings = Object.keys(props.settings).map((key) => {
        let setting = props.settings[key];
        switch (setting.dataType) {
            case 'percent':
                return <PercentSetting setting={setting} key={setting.outputName} handleSettingChange={props.handleSettingChange}/>;
            case 'number':
                return <NumberSetting setting={setting} key={setting.outputName} handleSettingChange={props.handleSettingChange}/>;
            case 'bool':
                return <BoolSetting setting={setting} key={setting.outputName} handleSettingChange={props.handleSettingChange}/>;
            case 'numberArray':
                return <NumberArraySetting setting={setting} key={setting.outputName} handleSettingChange={props.handleSettingChange}/>;
            case 'path':
                return <PathSetting setting={setting} key={setting.outputName} handleSettingChange={props.handleSettingChange}/>;
            default:
                console.log("Unrecognized dataType is causing a setting to not display");
                return null;
        };
    });

    return (
        <div className='SettingsList'>
            {addedSettings}
        </div>
        
    )
 }
