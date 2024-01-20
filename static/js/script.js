$(document).ready(function() {
    // Function to handle input changes
    $("#movie_name").on("input", function() {
        var userInput = $(this).val().trim();
    
        // Send AJAX request to fetch movie suggestions
        $.ajax({
            url: "/get_movie_suggestions",
            type: "POST",
            data: { input: userInput },
            success: function(response) {
                // Clear suggestions container
                $("#suggestions-container").html("");
    
                // Display a maximum of 10 suggestions in the suggestions-container
                response.slice(0, 10).forEach(function(movie) {
                    $("#suggestions-container").append('<div class="movie-suggestion">' + movie.title + '</div>');
                });
            }
        });
    });

    

    // Function to handle suggestion selection
    $("#suggestions-container").on("click", ".movie-suggestion", function() {
        var selectedMovie = $(this).text();

        
        // Set the selected movie in the movie_name input
        $("#movie_name").val(selectedMovie);
        $("#suggestions-container").html("");  // Clear suggestions container

        // Send AJAX request to fetch genres for the selected movie
        $.ajax({
            url: "/get_movie_genres",
            type: "POST",
            data: { movie_name: selectedMovie },
            success: function(response) {
                // Set the fetched genres in the movie_genres input
                $("#movie_genres").val(response.genres);
            }
        });
    });

    // Enhance form submission handling
$("#recommendationForm").submit(function(event) {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Get the form data
    var formData = {
        movie_name: $("#movie_name").val(),
        movie_genres: $("#movie_genres").val()
    };

    // Submit the form using AJAX
    $.ajax({
        url: "/",
        type: "POST",
        data: formData,
        dataType: 'json',  
        
        success: function(response) {
            // Remove existing recommendations before appending new ones
            $("#recommendations-body").empty();

            // Display recommendations in the recommendations container with animation
            response.forEach(function(movie, index) {
                var row = `<tr class="animated-row">
                                <td>${movie.title}</td>
                                <td>${movie.genres}</td>
                                <td>${movie.avg_rating}</td>
                        </tr>`;
                // Add a slight delay for each row to create a staggered effect
                setTimeout(function() {
                    $("#recommendations-body").append(row);
                    // Add the animated class after appending to trigger the animation
                    $("#recommendations-table tbody tr:last-child").addClass('animated-row');
                }, index * 100); // Adjust the delay as needed
            });

            // Show the table after appending recommendations
            $("#recommendations-table").fadeIn();
        }}
    )})
})

