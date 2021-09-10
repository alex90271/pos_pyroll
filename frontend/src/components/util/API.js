const API = {
    send() {
      fetch('http://localhost:5000/v01/config') 
        .then(response => response.json())
        .then(data => console.log(data))
    },

    test(firstDay, lastDay, jobcodes = 0, employees = 0) {
      return fetch(`http://localhost:5000/v01/data/${firstDay}/${lastDay}/labor_nightly/${jobcodes}/${employees}/False`)
        .then(response => response.json());
    },

    consoleLogConfig() {
      fetch('http://localhost:5000/v01/config')
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
}
export default API;

