function makeSearch(searchInputId, selectId) {
    var search = document.getElementById(searchInputId);
    var select = document.getElementById(selectId);

    search.oninput = function () {
        var query = search.value.toLowerCase();
        var options = select.getElementsByTagName("option");
        for (var i = 0; i < options.length; i++) {
            var option = options[i];
            if (option.innerHTML.toLowerCase().indexOf(query) > -1) {
                option.style.display = "inline";
            } else {
                option.style.display = "none";
            }
        }
    };
}

if (document.getElementById('mother_search')) {
    makeSearch('mother_search', 'mother');
    makeSearch('father_search', 'father');
}

if (document.getElementById('receiver_search')) {
    makeSearch('receiver_search', 'receiver_id');
}