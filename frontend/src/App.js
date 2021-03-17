import './App.css';
import React, { useState } from 'react';
import Calendar from './components/calendar/calendar';
import SettingsList from './components/settingsList/settingsList';
import Test from './components/test/test';
import { defaultSettingsArray } from './defaultSettingsArray';

function App() {
  const [settings, setSettings] = useState(defaultSettingsArray);
  return (
    <div>
      <Calendar/>
      <SettingsList
      settings={settings}/>
    </div>
  );
}

export default App;
