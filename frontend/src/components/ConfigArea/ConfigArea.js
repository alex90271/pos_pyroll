import './ConfigArea.css';
import React, { useState } from 'react';
import Calendar from '../calendar/calendar';
import PrintArea from '../PrintArea/PrintArea.js';
import SettingsList from '../settingsList/settingsList';
import { defaultSettingsObject } from '../../defaultSettingsObject';


export default function ConfigArea(props) {

    const [settings, setSettings] = useState(defaultSettingsObject);
    const [canPrint, setCanPrint] = useState(false);

    function handleSettingChange(newSetting) {
        if (newSetting.displayName && newSetting.outputName && newSetting.dataType && (typeof(newSetting.value) != 'undefined')) {
          setSettings((prevSettings) => ({
            ...prevSettings, [newSetting.outputName]: newSetting
          }));
        } else {
          throw Error("Something went wrong. (the newSetting object is not complete)");
        }
      }



    return (
        <div className="ConfigArea">
            <Calendar
            canPrint={canPrint}
            setCanPrint={setCanPrint}
            />
            <PrintArea
            canPrint={canPrint}
            print={props.print}
            />
            <SettingsList
            settings={settings}
            handleSettingChange={handleSettingChange}
            />
        </div>
    );
}