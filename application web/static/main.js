// main.js

function filterMusicList() {
    var input = document.getElementById("music_name").value.toLowerCase();
    var musicList = document.getElementById("music_list");
    var items = musicList.getElementsByTagName("li");

    for (var i = 0; i < items.length; i++) {
        var musicTitle = items[i].textContent || items[i].innerText;
        if (musicTitle.toLowerCase().indexOf(input) > -1) {
            items[i].style.display = "";
        } else {
            items[i].style.display = "none";
        }
    }
}
