function makeSearch(searchInputId, selectId) {
    const search = document.getElementById(searchInputId);
    const select = document.getElementById(selectId);

    search.oninput = function () {
        const query = search.value.toLowerCase();
        const options = select.getElementsByTagName("option");
        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            if (option.innerHTML.toLowerCase().indexOf(query) > -1) {
                option.style.display = "";
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