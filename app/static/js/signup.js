$(document).ready(function() {

    $('#register').click(function() {
 
        $.ajax({
            url: '/signup',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
                var result = JSON.parse(response).message;
                if (result == 'Success!') {
                  window.location.assign('/home');
                } else {
                  $('#error').html('Error! ' + result);
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
    $(function() {
        $("form input").keypress(function (e) {
            if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
                $('#register').click();
                return false;
            } else {
                return true;
            }
        });
    });
});