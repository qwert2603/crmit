function moveItems(origin, dest) {
    $(origin).find(':selected').appendTo(dest);
}

$('#left').click(function () {
    moveItems('#others', '#in_group');
});

$('#right').on('click', function () {
    // todo: don't move student if he attended lesson or paid ever.
    moveItems('#in_group', '#others');
});

function selectAll() {
    var in_group = document.getElementById("in_group");

    for (var i = 0; i < in_group.options.length; i++) {
        in_group.options[i].selected = true;
    }
}