function moveItems(origin, dest) {
    var find = $(origin).find(':selected');
    // prefix '(f)' is always first in selected.
    // i hope.
    const label = find['0'].label;
    if (label.indexOf('(f)') >= 0) {
        alert(label + ' уже посещал занятия или вносил оплату!');
    }
    else {
        find.appendTo(dest);
    }
}

$('#left').click(function () {
    moveItems('#others', '#in_group');
});

$('#right').on('click', function () {
    moveItems('#in_group', '#others');
});

function selectAll() {
    var in_group = document.getElementById("in_group");

    for (var i = 0; i < in_group.options.length; i++) {
        in_group.options[i].selected = true;
    }
}