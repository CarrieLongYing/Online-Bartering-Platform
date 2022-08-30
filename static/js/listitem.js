$("#platform_type_selector").show()
$("#media_selector").show()
$("#card_selector").hide()

$('#game_type').change(function () {
    var value = this.value;
    if (value == 'Video Game') {
        $("#platform_type_selector").show()
        $("#media_selector").show()
        $("#card_selector").hide()
    } else if (value == 'Playing Card Game') {
        $("#platform_type_selector").hide()
        $("#media_selector").hide()
        $("#card_selector").hide()
    } else if (value == 'Collectible Card Game') {
        $("#platform_type_selector").hide()
        $("#media_selector").hide()
        $("#card_selector").show()
    } else if (value == 'Computer Game') {
        $("#platform_type_selector").show()
        $("#media_selector").hide()
        $("#card_selector").hide()
    } else if (value == 'Board Game') {
        $("#platform_type_selector").hide()
        $("#media_selector").hide()
        $("#card_selector").hide()
    }

});