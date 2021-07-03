const API = {
    send() {
        fetch('127.0.0.1:5000/v01/config/') 
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.blob();
            })
            .then(myBlob => {
                console.log(myBlob);
            })
    }
}

export default API;