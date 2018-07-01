function goBackInHistory() {
    var prevUrl = document.referrer;
    if (prevUrl) window.location.replace(prevUrl);
}

function askDelete(entity_name, delete_url) {
    if (confirm('удалить ' + entity_name + '?')) {
        window.location.replace(delete_url);
    }
}