$('#home-search').focus(function() {
    if ($('#home-search').val().toLowerCase() == 'search') $('#home-search').val('')
});
$('#recommendation').focus(function() {
    if ($('#recommendation').val().toLowerCase() == 'twitter handle') $('#recommendation').val('')
});

$('#home-search').keypress(function (e) {
    var key = e.which;
    if(key == 13) {
        search_tweets()
        return false;
    }
});

$('#basic-addon2').click(function() {
    search_tweets()
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

function present_tweet_view(data) {
    id = data.fields.id
    username = data.fields.user
    text = data.fields.text
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
    markup += '<span class="text-muted"><i class="fa fa-clock-o" aria-hidden="true"></i> {{ entry[created_at] }}</span>';
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
