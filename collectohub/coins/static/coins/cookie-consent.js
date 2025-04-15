function acceptCookies() {
    document.getElementById('cookie-consent-banner').style.display = 'none';
    localStorage.setItem('cookieConsent', 'accepted');
}

window.onload = function() {
    if (!localStorage.getItem('cookieConsent')) {
        document.getElementById('cookie-consent-banner').style.display = 'block';
    }
} 