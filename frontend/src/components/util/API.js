const API = {
    send() {
      fetch('http://localhost:5000/v01/config') 
        .then(response => response.json())
        .then(data => console.log(data))
    },
    
    getExampleObject() {
        return {
            "0":{
            "LASTNAME":"Alder",
            "FIRSTNAME":"Alex",
            "JOB_NAME":"Bitch",
            "HOURS":4.27,
            "OVERHRS":0.0,
            "SRVTIPS":0.0,
            "TIPOUT":40.422720771,
            "DECTIPS":34.894,
            "MEALS":null
          },
            "1": {
            "LASTNAME":"Baker",
            "FIRSTNAME":"Colby",
            "JOB_NAME":"Server",
            "HOURS":4.27,
            "OVERHRS":0.0,
            "SRVTIPS":0.0,
            "TIPOUT":40.0902720771,
            "DECTIPS":7.589,
            "MEALS":null
          }}
    }
}

export default API;