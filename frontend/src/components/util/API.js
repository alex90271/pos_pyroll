const API = {
    settings() {
      return fetch('http://localhost:5000/v01/config/SETTINGS') 
        .then(response => response.json());
    },

    process(firstDay, lastDay, jobcodes = 0, employees = 0) {
      return fetch(`http://localhost:5000/v01/data/${firstDay}/${lastDay}/labor_nightly/${jobcodes}/${employees}/False`)
        .then(response => response.json());
    },

    consoleLogConfig() {
      fetch('http://localhost:5000/v01/config/SETTINGS')
        .then(response => response.json())
        .then(data => console.log(data));
    },

    employees() {
      return fetch('http://localhost:5000/v01/employees')
        .then(response => response.json());
    },

    jobcodes() {
      return fetch('http://localhost:5000/v01/jobcodes')
        .then(response => response.json());
    },
    saveSettings(newSettings) {
      const formattedSettings = formatSettingsForExport(newSettings);
      fetch(`http://localhost:5000/v01/config/SETTINGS${formattedSettings}`, {
        method: "POST"
      })
    },
}
export default API;

const formatSettingsForExport = (newSettings) => {
  let input = Object.assign({}, newSettings);
  let output = {};
  for (const currentSetting in input) {
    const outputName = input[currentSetting].outputName;
    const inputValue = input[currentSetting].value;
    let outputValue;
    if (inputValue instanceof Array) {
      outputValue = inputValue.map((currentValue) => {
        return currentValue.value;   
      }).join(",");
    } else {
      outputValue = inputValue;
    }
    output[outputName] = outputValue;
  }
  return JSON.stringify(output);
}

