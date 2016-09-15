$('#home-search').focus(function() {
    if ($('#home-search').val().toLowerCase() == 'search') $('#home-search').val('')
});
$('#recommendation').focus(function() {
    if ($('#recommendation').val().toLowerCase() == 'twitter handle') $('#recommendation').val('')
});