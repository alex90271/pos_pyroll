import './App.css';
import React, { useState } from 'react';
import Calendar from './components/calendar/calendar';
import SettingsList from './components/settingsList/settingsList';
import Test from './components/test/test';
import { defaultSettingsObject } from './defaultSettingsObject';

function App() {

  const [settings, setSettings] = useState(defaultSettingsObject);

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
    <div>
      <Calendar/>
      <SettingsList
      settings={settings}
      handleSettingChange={handleSettingChange}
      />
    </div>
  );
}

export default App;
