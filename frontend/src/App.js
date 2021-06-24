import './App.css';
import React, { useState } from 'react';
import Calendar from './components/calendar/calendar';
import PrintArea from './components/PrintArea/PrintArea';
import SettingsList from './components/settingsList/settingsList';
import Test from './components/test/test';
import API from './components/util/API.js';
import { defaultSettingsObject } from './defaultSettingsObject';

function App() {

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

  function print() {
    API.send();
  }

  return (
    <div>
      <Calendar
      canPrint={canPrint}
      setCanPrint={setCanPrint}
      />
      <PrintArea
      canPrint={canPrint}
      print={print}
      />
      <SettingsList
      settings={settings}
      handleSettingChange={handleSettingChange}
      />
    </div>
  );
}

export default App;
