$('#home-search').focus(function() {
    if ($('#home-search').val().toLowerCase() == 'search') $('#home-search').val('')
});
$('#user-search').focus(function() {
    if ($('#user-search').val().toLowerCase() == 'search') $('#user-search').val('')
});
$('#recommendation').focus(function() {
    if ($('#recommendation').val().toLowerCase() == 'enter a twitter handle') $('#recommendation').val('')
});
$('#email').focus(function() {
    if ($('#email').val().toLowerCase() == 'email address') $('#email').val('')
});

$('#home-search').keypress(function (e) {
    var key = e.which;
    if(key == 13) {
        search_tweets()
        return false;
    }
});

$('#user-search').keypress(function (e) {
    var key = e.which;
    if(key == 13) {
        search_users()
        return false;
    }
});

$('#recommendation').keypress(function (e) {
    var key = e.which;
    if(key == 13) {
        recommend_user($('#recommendation').val())
        return false;
    }
});

$('#basic-addon2').click(function() {
    search_tweets()
});

$('#basic-addon3').click(function() {
    search_users()
});


function search_tweets() {
    q = $('#home-search').val()
    url = 'https://u15ad1lqt7.execute-api.eu-west-1.amazonaws.com/prod?q=' + q

    $.ajax({
        url: url,
        success: function(data) {
            d = data.hits.hit
            markup = ''
            for (var i =0; i < d.length; i ++) {
                markup  += present_tweet_view(d[i])
            }
            $('#tweets').html(markup)
        }
    });
}

function search_users() {

}

function present_tweet_view(data) {
    id = data.fields.id
    username = data.fields.user
    text = data.fields.text
//    time = data.fields.created_at
//    image = data.fields.image
    markup = ' <div class="tweet-card" style="height:auto;margin-top:15px;padding:0px 20px;">';
    markup += '<div class="row wrapper" style="">';
    markup += '<div class="col-md-1" style="height:100%;padding-top: 50px;">';
    markup += '<a class="media-left" href="https://twitter.com/' + username + '" style="" target="_blank">';
    markup += '</a>';
    markup += '</div>';
    markup += '<div class="col-md-11" style="padding: 20px;">';
    markup += '<span class="media-heading"><a href="https://twitter.com/' + username + '" target="_blank">@' + username + '</a></span> deleted this tweet:';
    markup += '<div class="blockquote">';
    markup += '<a href="/tweet/' + id + '"><p class="m-b-0">' + text + '</p> </a>';
    markup += '</div>';
    markup += '<hr>';
    markup += '<span class="text-muted"><i class="fa fa-clock-o" aria-hidden="true"></i> '  + '</span>';
    markup += '&nbsp;.&nbsp;';
        //markup += '<span class="text-muted">via {{ entry.get('source') }}</span>';
    markup += '<span class="links">';
    //markup += '<a target="_blank" href="https://twitter.com/intent/tweet?hashtags=twoops&original_referer=https%3A%2F%2Fcodeforafrica.tech&ref_src=twsrc%5Etfw&tw_p=tweetbutton&text=.@{{ entry['username'] }}">Reply to @{{ entry['username'] }}</a>';
    markup += '&nbsp;.&nbsp;';
    //markup += '<a target="_blank" href="https://twitter.com/intent/tweet?hashtags=twoops&original_referer=https%3A%2F%2Fcodeforafrica.tech&ref_src=twsrc%5Etfw&tw_p=tweetbutton&text=.@{{ entry['username'] }} deleted this tweet: {{ entry['message'].decode("utf-8") }}" >Share on Twitter</a>';
    markup += '</span>';
    markup += ' </div>';
    markup += '</div>';
    markup += '</div>';
    return markup
}

$('#recommend-button').click(function() {
    recommend_user($('#recommendation').val())
})

$('#alert-button').click(function() {
    subscribe($('#email').val())
})

function recommend_user(handle) {
    if (handle != '') {
        url = '/recommend?handle=' + handle
        $.ajax({
            url: url,
            success: function(data) {
                if (data.success) {
                    $('.success').css('display', 'block')
                    $('.error').css('display', 'none')
                } else {
                    $('.success').css('display', 'none')
                    $('.error').css('display', 'block')
                }
            }
        });
    }
}

function subscribe(email) {
    if (email != '') {
        user_id = $('#user_id').val()
        url = '/subscribe-to-alerts?email=' + email + '&user_id=' + user_id
        $.ajax({
            url: url,
            method: 'GET',
            data: $('#alert-form').serialize(),
            success: function(data) {
                if (data.success) {
                    $('.success').css('display', 'block')
                    $('.error').css('display', 'none')
                } else {
                    $('.success').css('display', 'none')
                    $('.error').css('display', 'block')
                }
            }
        });
    }
}