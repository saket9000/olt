// AJAX for posting

// $("#submit").click(function(e){
//     e.preventDefault();
//     var csrftoken = getCookie('csrftoken');
//     var batch = $('#batch').val();

//     $.ajax({
//        url : window.location.href, // the endpoint,commonly same url
//        type : "POST", // http method
//        data : { csrfmiddlewaretoken : csrftoken, 
//        batch : batch,
//  },

//  success : function(json) {
//  console.log(json); 

//  alert('Hi   '+json['email'] +'!.' + '  You have entered password:'+ json['password']);
//  },
//  error : function(xhr,errmsg,err) {
//  console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
//  }
// })
// });





function get_page_data(year) {
    console.log("create post is working!") // sanity check
    $.ajax({
        url : "/batch-ajax", // the endpoint
        type : "POST", // http method
        data : { batch : year }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            //$('#post-text').val(''); // remove the value from the input
            //console.log(json); // log the returned json to the console
            //$('#table').html(json.tdata)
            //$('#page_list').html(json.pdata)
            $('#post-text').val(json);
            console.log(json);
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

// This function gets cookie with a given name
$("html").on('change', 'select#year', function(event){
    event.preventDefault();
    console.log("I see you")  // sanity check
    console.log($("select#year").value);
    get_page_data($("select#year").value);
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

/*
The functions below will create a header with csrftoken
*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});