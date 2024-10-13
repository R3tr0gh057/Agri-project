document.addEventListener("DOMContentLoaded", function() {
    const socket = io();

    // Update data dynamically
    socket.on('change-detected', function(data) {
        const updated_temperature = data.new_temp;
        const updated_humidity = data.new_hum;
        document.getElementById("temperature").innerHTML = updated_temperature
        document.getElementById("humidity").innerHTML = updated_humidity;
    });
});