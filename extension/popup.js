const analyzeBtn = document.getElementById('analyzeBtn');
const messageEl = document.getElementById('message');
const resultsEl = document.getElementById('results');
const accountIdEl = document.getElementById('accountId');
const summaryTextEl = document.getElementById('summaryText');

const API_BASE_URL = 'http://localhost:5001/api';

// Listen for the account ID sent from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.accountId) {
        fetchAccountSummary(request.accountId);
    } else {
        messageEl.textContent = 'No account ID found on this page. Please ensure an ID like "C12345678" is visible.';
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Page';
    }
});

analyzeBtn.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';
    messageEl.textContent = 'Searching for an account ID on the page...';
    resultsEl.classList.add('hidden');

    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
            // This is the function that will be executed on the page
            // It's the same logic as in content.js
            const bodyText = document.body.innerText;
            const accountRegex = /(C\d{7,9})\b/;
            const match = bodyText.match(accountRegex);
            const accountId = match ? match[0] : null;
            chrome.runtime.sendMessage({ accountId });
        }
    });
});

async function fetchAccountSummary(accountId) {
    messageEl.textContent = `Found Account: ${accountId}. Fetching AI summary...`;
    
    try {
        const response = await fetch(`${API_BASE_URL}/account-summary/${accountId}`);
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        const data = await response.json();

        // Display the results
        accountIdEl.textContent = `Analysis for: ${data.account_id}`;
        summaryTextEl.textContent = data.summary;
        messageEl.classList.add('hidden');
        resultsEl.classList.remove('hidden');

    } catch (error) {
        console.error('Error fetching summary:', error);
        messageEl.textContent = `Error: Could not fetch summary for ${accountId}. Is the backend running?`;
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Page';
    }
}
