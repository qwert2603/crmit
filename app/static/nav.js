function goBackInHistory() {
    window.history.back();
}

function askDelete(entity_name, delete_url) {
    if (confirm('удалить ' + entity_name + '?')) {
        window.location.replace(delete_url)
    }
}