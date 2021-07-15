const API = {
    send() {
        fetch('http://localhost:5000/v01/config') 
            .then(response => response.json())
            .then(data => console.log(data))
    }
}

export default API;