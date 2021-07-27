import './App.css';
import React, { useState } from 'react';
import Test from './components/test/test';
import API from './components/util/API.js';
import ConfigArea from './components/ConfigArea/ConfigArea';
import DataView from './components/DataView/DataView';

function App() {

  function print() {
    API.send();
  }

  return (
    <div className="App">
      <ConfigArea
      print={print}
      />
      <DataView />
    </div>
  );
}

export default App;
