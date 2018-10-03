function goBackInHistory() {
    var prevUrl = document.referrer;
    if (prevUrl) window.location.replace(prevUrl);
}

function askDelete(entity_name, delete_url) {
    if (confirm('удалить ' + entity_name + '?')) {
        window.location.replace(delete_url);
    }
}

function askLogoutApp(success_url) {
    if (confirm('завершить все сессии в мобильном приложении?')) {
        window.location.replace(success_url);
    }
}