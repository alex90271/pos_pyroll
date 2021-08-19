const API = {
    send() {
      fetch('http://localhost:5000/v01/config') 
        .then(response => response.json())
        .then(data => console.log(data))
    },

    test(firstDay, lastDay) {
      return fetch(`http://localhost:5000/v01/data/${firstDay}/${lastDay}/labor_main/False`)
        .then(response => response.json());
    },
}
export default API;

