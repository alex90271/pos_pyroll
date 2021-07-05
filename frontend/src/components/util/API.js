const API = {
    send() {
        fetch('127.0.0.1:5000/v01/config/') 
            .then(response => response.json())
            .then(data => console.log(data))
    }
}

export default API;