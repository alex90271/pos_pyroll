import React, { useState } from 'react';
import './settingsList.css';
import PercentSetting from '../SettingComponents/percentSetting/percentSetting';
import NumberSetting from '../SettingComponents/NumberSetting/NumberSetting';
import BoolSetting from '../SettingComponents/BoolSetting/BoolSetting';
import NumberArraySetting from '../SettingComponents/NumberArraySetting/NumberArraySetting';
import PathSetting from '../SettingComponents/PathSetting/PathSetting';

export default function SettingsList(props) {
    let addedSettings;
    addedSettings = props.settings.map((setting) => {
        switch (setting.dataType) {
            case 'percent':
                return <PercentSetting setting={setting}/>;
            case 'number':
                return <NumberSetting setting={setting}/>;
            case 'bool':
                return <BoolSetting setting={setting}/>;
            case 'numberArray':
                return <NumberArraySetting setting={setting}/>;
            case 'path':
                return <PathSetting setting={setting}/>;
            default:
                console.log("Unrecognized dataType is causing a setting to not display");
                return undefined;
        };
    });
    return (
        <div className='SettingsList'>
            <h2>
                Settings
            </h2>
            {addedSettings}
        </div>
    );
};

