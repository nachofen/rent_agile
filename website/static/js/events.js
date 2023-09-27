$(document).ready(function() {
    // Add a click event listener to all delete buttons with the class "delete-vehiculo"
    $(".delete-vehiculo").click(function() {
        // Get the vehicle ID from the data-vehiculo-id attribute
        var vehiculoId = $(this).data("vehiculo-id");

        // Send an AJAX request to delete the vehicle
        $.ajax({
            type: "POST", // Use POST or DELETE method, depending on your server configuration
            url: "/delete-vehiculo/" + vehiculoId, // Replace with your server route for deleting a vehicle
            success: function(response) {
                // Handle success, e.g., remove the deleted vehicle from the list
                alert("Vehicle deleted successfully");
                location.reload(); // Refresh the page to reflect the updated list
            },
            error: function(error) {
                // Handle error, if any
                alert("Error deleting vehicle: " + error);
            }
        });
    });
});