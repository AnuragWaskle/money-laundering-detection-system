// This script is injected into the active webpage.
// Its goal is to find an account ID. This is a simple example
// that looks for a specific pattern. A real-world version would be
// more robust.

function findAccountId() {
    const bodyText = document.body.innerText;
    // Look for a pattern like "C" followed by 7-9 digits (e.g., C12345678)
    const accountRegex = /(C\d{7,9})\b/; 
    const match = bodyText.match(accountRegex);
    
    if (match && match[0]) {
        return match[0];
    }
    return null;
}

// Send the found account ID back to the popup script
chrome.runtime.sendMessage({ accountId: findAccountId() });
