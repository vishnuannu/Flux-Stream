const API_URL = window.location.origin;

function toggleTheme() {
    const html = document.documentElement;
    const themes = ['red', 'green', 'purple', 'sky', 'orange', 'pink', 'yellow'];
    const currentTheme = html.getAttribute('data-theme');
    const currentIndex = themes.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themes.length;
    const newTheme = themes[nextIndex];
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

const savedTheme = localStorage.getItem('theme') || 'red';
document.documentElement.setAttribute('data-theme', savedTheme);

document.getElementById('threads').addEventListener('input', function() {
    document.getElementById('thread-value').textContent = this.value;
});


function switchTab(tab, evt) {
    const tabs = document.querySelectorAll('.tab-panel');
    const buttons = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(`${tab}-tab`).classList.add('active');
    evt.target.closest('.tab-btn').classList.add('active');
}

function toggleProxyInput() {
    const useProxy = document.getElementById('use-proxy').checked;
    const container = document.getElementById('proxy-input-container');
    
    if (useProxy) {
        container.classList.remove('hidden');
    } else {
        container.classList.add('hidden');
    }
}

function toggleBulkUrls() {
    const useBulk = document.getElementById('use-bulk-urls').checked;
    const singleContainer = document.getElementById('single-url-container');
    const bulkContainer = document.getElementById('bulk-url-container');
    
    if (useBulk) {
        singleContainer.classList.add('hidden');
        bulkContainer.classList.remove('hidden');
    } else {
        singleContainer.classList.remove('hidden');
        bulkContainer.classList.add('hidden');
    }
}

function updateStatus(message) {
    document.getElementById('status').textContent = message;
}

function updateCurrentMac(mac, url = null) {
    const display = document.getElementById('current-mac-display');
    const macValue = document.getElementById('current-mac-value');
    const urlValue = document.getElementById('current-url-value');
    if (mac) {
        display.style.display = 'block';
        macValue.textContent = mac;
        if (url) {
            urlValue.textContent = url;
        }
    } else {
        display.style.display = 'none';
        macValue.textContent = '-';
        urlValue.textContent = '-';
    }
}

function updateOutput(message, append = false) {
    const output = document.getElementById('output');
    if (append) {
        output.innerHTML += message + '\n';
    } else {
        output.innerHTML = message;
    }
    output.scrollTop = output.scrollHeight;
}

function formatMacInfo(result) {
    if (!result.valid) {
        return `<div class="invalid-mac">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 20px; height: 20px; display: inline-block; vertical-align: middle;">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
            <strong>Invalid MAC:</strong> ${result.mac}
        </div>`;
    }
    
    let info = `<div class="valid-mac">
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 24px; height: 24px; color: var(--success);">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
    <strong style="font-size: 1.1em;">VALID MAC FOUND</strong>
</div>

<div style="background: var(--bg-tertiary); padding: 12px; border-radius: 8px; margin: 10px 0;">
    <div style="font-size: 0.9em; color: var(--text-secondary);">MAC Address</div>
    <div style="font-size: 1.2em; font-weight: 700; color: var(--accent); font-family: monospace;">${result.mac}</div>
</div>`;
    
    if (result.account_info) {
        info += `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 12px 0;">`;
        
        if (result.account_info.phone) {
            info += `<div style="background: var(--bg-tertiary); padding: 10px; border-radius: 8px;">
                <div style="font-size: 0.85em; color: var(--text-secondary);">Expiry Date</div>
                <div style="font-weight: 600; color: var(--success);">${result.account_info.phone}</div>
            </div>`;
        }
        
        if (result.account_info.status) {
            info += `<div style="background: var(--bg-tertiary); padding: 10px; border-radius: 8px;">
                <div style="font-size: 0.85em; color: var(--text-secondary);">Status</div>
                <div style="font-weight: 600;">${result.account_info.status}</div>
            </div>`;
        }
        
        if (result.account_info.tariff_plan) {
            info += `<div style="background: var(--bg-tertiary); padding: 10px; border-radius: 8px;">
                <div style="font-size: 0.85em; color: var(--text-secondary);">Tariff Plan</div>
                <div style="font-weight: 600;">${result.account_info.tariff_plan}</div>
            </div>`;
        }
        
        info += `</div>`;
    }
    
    if (result.channels_info && (result.channels_info.total_channels > 0 || result.channels_info.total_categories > 0)) {
        info += `<div style="margin: 16px 0;">
            <div style="font-weight: 700; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 18px; height: 18px;">
                    <rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect>
                    <polyline points="17 2 12 7 7 2"></polyline>
                </svg>
                Content Library
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">`;
        
        if (result.channels_info.total_channels !== undefined && result.channels_info.total_channels > 0) {
            info += `<div style="background: linear-gradient(135deg, var(--accent), var(--accent-hover)); padding: 12px; border-radius: 8px; color: white; text-align: center;">
                <div style="font-size: 1.8em; font-weight: 700;">${result.channels_info.total_channels}</div>
                <div style="font-size: 0.85em; opacity: 0.9;">Channels</div>
            </div>`;
        }
        
        if (result.channels_info.total_categories !== undefined && result.channels_info.total_categories > 0) {
            info += `<div style="background: linear-gradient(135deg, var(--success), #059669); padding: 12px; border-radius: 8px; color: white; text-align: center;">
                <div style="font-size: 1.8em; font-weight: 700;">${result.channels_info.total_categories}</div>
                <div style="font-size: 0.85em; opacity: 0.9;">Categories</div>
            </div>`;
        }
        
        if (result.channels_info.total_vod !== undefined && result.channels_info.total_vod > 0) {
            info += `<div style="background: linear-gradient(135deg, var(--warning), #d97706); padding: 12px; border-radius: 8px; color: white; text-align: center;">
                <div style="font-size: 1.8em; font-weight: 700;">${result.channels_info.total_vod}</div>
                <div style="font-size: 0.85em; opacity: 0.9;">VOD Items</div>
            </div>`;
        }
        
        info += `</div></div>`;
        
        if (result.channels_info.categories && result.channels_info.categories.length > 0) {
            info += `<div style="margin-top: 12px;">
                <details style="background: var(--bg-tertiary); padding: 10px; border-radius: 8px;">
                    <summary style="cursor: pointer; font-weight: 600; user-select: none;">View Categories (${result.channels_info.categories.length})</summary>
                    <div style="margin-top: 10px; display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px;">`;
            
            result.channels_info.categories.forEach(cat => {
                const count = cat.count || 0;
                const countText = count > 0 ? ` <span style="color: var(--accent); font-weight: 600;">(${count})</span>` : '';
                info += `<div style="padding: 6px 10px; background: var(--bg-secondary); border-radius: 6px; font-size: 0.9em;">
                    ${cat.title || cat.name || 'Unknown'}${countText}
                </div>`;
            });
            
            info += `</div></details></div>`;
        }
    }
    
    info += `<div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border); font-size: 0.85em; color: var(--text-secondary);">
        <div>Endpoint: ${result.endpoint}</div>
        <div>Status: ${result.status_code}</div>
    </div>`;
    
    info += '</div>';
    return info;
}

async function checkSingleMac() {
    const useBulk = document.getElementById('use-bulk-urls').checked;
    let urls = [];
    
    if (useBulk) {
        const urlListText = document.getElementById('url-list').value.trim();
        if (!urlListText) {
            alert('Please enter URLs');
            return;
        }
        urls = urlListText.split(/[\n,]+/).map(u => u.trim()).filter(u => u);
    } else {
        const url = document.getElementById('stalker-url').value.trim();
        if (!url) {
            alert('Please enter URL');
            return;
        }
        urls = [url];
    }
    
    const mac = document.getElementById('custom-mac').value.trim();
    
    if (!mac) {
        alert('Please enter MAC address');
        return;
    }
    
    updateCurrentMac(mac, urls.length === 1 ? urls[0] : `${urls.length} URLs`);
    updateStatus(`Checking MAC against ${urls.length} URL(s)...`);
    updateOutput('<div class="checking">⏳ Checking MAC address...</div>');
    
    try {
        const proxies = document.getElementById('use-proxy').checked ? 
            document.getElementById('proxy-list').value.trim().split('\n').map(p => p.trim()).filter(p => p) : [];
        
        const response = await fetch(`${API_URL}/check_mac_multiple_urls`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ urls, mac, proxies })
        });
        
        const data = await response.json();
        
        if (data.valid_result) {
            updateOutput(formatMacInfo(data.valid_result));
            updateStatus('Valid MAC Found!');
        } else {
            let output = `<div style="margin-bottom: 12px;"><strong>Checked ${urls.length} URL(s) - No valid results</strong></div>`;
            data.results.forEach((result, idx) => {
                output += formatMacInfo(result);
            });
            updateOutput(output);
            updateStatus('MAC Invalid on all URLs');
        }
        updateCurrentMac(null);
    } catch (error) {
        updateOutput(`<div class="invalid-mac">❌ Error: ${error.message}</div>`);
        updateStatus('Error occurred');
        updateCurrentMac(null);
    }
}

async function checkMacList() {
    const url = document.getElementById('stalker-url').value.trim();
    const macList = document.getElementById('mac-list').value.trim();
    const threads = parseInt(document.getElementById('threads').value);
    
    if (!url || !macList) {
        alert('Please enter both URL and MAC list');
        return;
    }
    
    const macs = macList.split('\n').map(m => m.trim()).filter(m => m);
    
    if (macs.length === 0) {
        alert('No valid MACs in the list');
        return;
    }
    
    let currentIndex = 0;
    const displayInterval = setInterval(() => {
        if (currentIndex < macs.length) {
            updateCurrentMac(macs[currentIndex], url);
            currentIndex++;
        }
    }, 100);
    
    updateStatus(`Checking ${macs.length} MACs with ${threads} threads...`);
    updateOutput('<div class="checking">⏳ Checking MAC list...</div>');
    
    try {
        const proxies = document.getElementById('use-proxy').checked ? 
            document.getElementById('proxy-list').value.trim().split('\n').map(p => p.trim()).filter(p => p) : [];
        
        const response = await fetch(`${API_URL}/check_macs_from_list`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, macs, threads, proxies })
        });
        
        const data = await response.json();
        
        clearInterval(displayInterval);
        updateCurrentMac(null);
        
        let output = `<strong>Checked ${data.results.length} MACs</strong><br><br>`;
        
        if (data.valid_mac_found) {
            output += formatMacInfo(data.valid_mac_found);
            output += '<br><strong>✋ Stopped checking after finding valid MAC</strong><br><br>';
        }
        
        data.results.forEach(result => {
            output += formatMacInfo(result);
        });
        
        updateOutput(output);
        updateStatus(data.valid_mac_found ? 'Valid MAC Found!' : 'Check Complete');
    } catch (error) {
        clearInterval(displayInterval);
        updateCurrentMac(null);
        updateOutput(`<div class="invalid-mac">❌ Error: ${error.message}</div>`);
        updateStatus('Error occurred');
    }
}

async function startSystemCheck() {
    const useBulk = document.getElementById('use-bulk-urls').checked;
    let urls = [];
    
    if (useBulk) {
        const urlListText = document.getElementById('url-list').value.trim();
        if (!urlListText) {
            alert('Please enter URLs');
            return;
        }
        urls = urlListText.split(/[\n,]+/).map(u => u.trim()).filter(u => u);
    } else {
        const url = document.getElementById('stalker-url').value.trim();
        if (!url) {
            alert('Please enter Stalker URL');
            return;
        }
        urls = [url];
    }
    
    const threads = parseInt(document.getElementById('threads').value);
    const maxAttempts = parseInt(document.getElementById('max-attempts').value);
    const stopOnFirst = document.getElementById('stop-on-first').checked;
    
    const generateRandomMac = () => {
        const prefix = "00:1A:79";
        const suffix = Array.from({length: 3}, () => 
            Math.floor(Math.random() * 256).toString(16).toUpperCase().padStart(2, '0')
        ).join(':');
        return `${prefix}:${suffix}`;
    };
    
    const displayInterval = setInterval(() => {
        updateCurrentMac(generateRandomMac(), urls.length === 1 ? urls[0] : `${urls.length} URLs`);
    }, 150);
    
    updateStatus(`System check running with ${threads} threads across ${urls.length} URL(s)...`);
    updateOutput('<div class="checking">⏳ System check in progress (00:1A:79:XX:XX:XX)...</div>');
    
    try {
        const proxies = document.getElementById('use-proxy').checked ? 
            document.getElementById('proxy-list').value.trim().split('\n').map(p => p.trim()).filter(p => p) : [];
        
        const response = await fetch(`${API_URL}/system_check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ urls, threads, max_attempts: maxAttempts, proxies, stop_on_first: stopOnFirst })
        });
        
        const data = await response.json();
        
        clearInterval(displayInterval);
        updateCurrentMac(null);
        
        let output = `<div style="background: var(--bg-tertiary); padding: 12px; border-radius: 8px; margin-bottom: 16px;">
            <strong>System Check Complete</strong><br>
            Total MACs Checked: <strong>${data.total_checked}</strong><br>
            Valid MACs Found: <strong style="color: var(--success);">${data.total_valid}</strong>
        </div>`;
        
        if (data.valid_macs && data.valid_macs.length > 0) {
            output += `<div style="margin-bottom: 12px; font-weight: 600; color: var(--success);">
                ✅ Found ${data.valid_macs.length} Valid MAC${data.valid_macs.length > 1 ? 's' : ''}
            </div>`;
            
            data.valid_macs.forEach((mac, index) => {
                output += `<div style="margin-bottom: 16px;">
                    <div style="font-size: 0.9em; color: var(--text-secondary); margin-bottom: 8px;">Valid MAC #${index + 1}</div>
                    ${formatMacInfo(mac)}
                </div>`;
            });
        } else {
            output += '<div class="checking" style="background: rgba(245, 158, 11, 0.1);">⚠️ No valid MAC found in the checked range. Try increasing max attempts or threads.</div>';
        }
        
        updateOutput(output);
        updateStatus(data.total_valid > 0 ? `Found ${data.total_valid} Valid MAC${data.total_valid > 1 ? 's' : ''}!` : 'No valid MAC found');
    } catch (error) {
        clearInterval(displayInterval);
        updateCurrentMac(null);
        updateOutput(`<div class="invalid-mac">❌ Error: ${error.message}</div>`);
        updateStatus('Error occurred');
    }
}

async function stopChecking() {
    try {
        await fetch(`${API_URL}/stop_checking`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        updateStatus('Checking stopped');
    } catch (error) {
        console.error('Error stopping check:', error);
    }
}

let workingProxiesList = [];

async function checkProxies() {
    const proxyList = document.getElementById('proxy-check-list').value.trim();
    
    if (!proxyList) {
        alert('Please enter proxy list');
        return;
    }
    
    const proxies = proxyList.split('\n').map(p => p.trim()).filter(p => p);
    
    if (proxies.length === 0) {
        alert('No valid proxies in the list');
        return;
    }
    
    workingProxiesList = [];
    document.getElementById('copy-proxies-btn').style.display = 'none';
    
    const batchSize = Math.min(50, Math.max(10, Math.floor(proxies.length / 10)));
    const threads = Math.min(20, Math.max(5, Math.floor(batchSize / 2)));
    
    document.getElementById('proxy-status').textContent = `Checking ${proxies.length} proxies...`;
    document.getElementById('working-proxies').innerHTML = '<strong>Working Proxies (0):</strong><br><br>';
    document.getElementById('not-working-proxies').innerHTML = '<strong>Not Working Proxies (0):</strong><br><br>';
    
    let workingCount = 0;
    let notWorkingCount = 0;
    let completed = 0;
    
    const checkBatch = async (batch) => {
        try {
            const response = await fetch(`${API_URL}/check_proxies`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ proxies: batch, threads: threads })
            });
            
            const data = await response.json();
            
            if (data.working.length > 0) {
                data.working.forEach(proxyData => {
                    workingProxiesList.push(proxyData.proxy);
                    workingCount++;
                    const workingBox = document.getElementById('working-proxies');
                    const currentContent = workingBox.innerHTML;
                    const headerMatch = currentContent.match(/<strong>Working Proxies \(\d+\):<\/strong>/);
                    const newHeader = `<strong>Working Proxies (${workingCount}):</strong>`;
                    const newLine = `✅ ${proxyData.proxy} <span style="color: var(--success)">(${(proxyData.response_time * 1000).toFixed(0)}ms)</span><br>`;
                    
                    if (headerMatch) {
                        workingBox.innerHTML = currentContent.replace(headerMatch[0], newHeader) + newLine;
                    } else {
                        workingBox.innerHTML = newHeader + '<br><br>' + newLine;
                    }
                });
                
                document.getElementById('copy-proxies-btn').style.display = 'block';
            }
            
            if (data.not_working.length > 0) {
                data.not_working.forEach(proxyData => {
                    notWorkingCount++;
                    const notWorkingBox = document.getElementById('not-working-proxies');
                    const currentContent = notWorkingBox.innerHTML;
                    const headerMatch = currentContent.match(/<strong>Not Working Proxies \(\d+\):<\/strong>/);
                    const newHeader = `<strong>Not Working Proxies (${notWorkingCount}):</strong>`;
                    const newLine = `❌ ${proxyData.proxy}<br>`;
                    
                    if (headerMatch) {
                        notWorkingBox.innerHTML = currentContent.replace(headerMatch[0], newHeader) + newLine;
                    } else {
                        notWorkingBox.innerHTML = newHeader + '<br><br>' + newLine;
                    }
                });
            }
            
            completed += batch.length;
            document.getElementById('proxy-status').textContent = `Checking... ${completed}/${proxies.length} - ${workingCount} working, ${notWorkingCount} failed`;
            
        } catch (error) {
            console.error('Batch check error:', error);
        }
    };
    
    const checkInBatches = async () => {
        for (let i = 0; i < proxies.length; i += batchSize) {
            const batch = proxies.slice(i, i + batchSize);
            await checkBatch(batch);
        }
        
        document.getElementById('proxy-status').textContent = `Check complete: ${workingCount} working, ${notWorkingCount} not working`;
    };
    
    await checkInBatches();
}

function copyWorkingProxies() {
    if (workingProxiesList.length === 0) {
        alert('No working proxies to copy');
        return;
    }
    
    const textToCopy = workingProxiesList.join('\n');
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        const btn = document.getElementById('copy-proxies-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
        </svg> Copied!`;
        
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        alert('Failed to copy: ' + err);
    });
}

let currentM3U = null;

async function convertStalkerToM3U() {
    const url = document.getElementById('stalker-convert-url').value.trim();
    const mac = document.getElementById('stalker-convert-mac').value.trim();
    
    if (!url || !mac) {
        alert('Please enter both Portal URL and MAC address');
        return;
    }
    
    document.getElementById('converter-status').textContent = 'Converting Stalker to M3U...';
    document.getElementById('converter-output').innerHTML = '<div class="checking">⏳ Converting Stalker/MAC to M3U playlist...</div>';
    document.getElementById('download-btn').style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/convert/stalker-to-m3u`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, mac })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentM3U = data.m3u_content;
            const output = `<div class="valid-mac">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 24px; height: 24px; color: var(--success);">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    <strong style="font-size: 1.1em;">Conversion Successful!</strong>
                </div>
                <div style="background: var(--bg-tertiary); padding: 12px; border-radius: 8px; margin: 10px 0;">
                    <div style="font-size: 0.9em; color: var(--text-secondary);">Total Channels</div>
                    <div style="font-size: 1.5em; font-weight: 700; color: var(--accent);">${data.total_channels}</div>
                </div>
                <div style="margin-top: 12px;">
                    <div style="font-weight: 600; margin-bottom: 8px;">M3U Preview (first 20 lines):</div>
                    <pre style="background: var(--bg-secondary); padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 0.85em; max-height: 300px;">${data.m3u_content.split('\n').slice(0, 20).join('\n')}${data.m3u_content.split('\n').length > 20 ? '\n...' : ''}</pre>
                </div>
            </div>`;
            document.getElementById('converter-output').innerHTML = output;
            document.getElementById('download-btn').style.display = 'inline-flex';
            document.getElementById('converter-status').textContent = `Converted ${data.total_channels} channels successfully!`;
        } else {
            document.getElementById('converter-output').innerHTML = `<div class="invalid-mac">❌ ${data.error}</div>`;
            document.getElementById('converter-status').textContent = 'Conversion failed';
        }
    } catch (error) {
        document.getElementById('converter-output').innerHTML = `<div class="invalid-mac">❌ Error: ${error.message}</div>`;
        document.getElementById('converter-status').textContent = 'Error occurred';
    }
}

async function convertXtreamToM3U() {
    const url = document.getElementById('xtream-url').value.trim();
    const username = document.getElementById('xtream-username').value.trim();
    const password = document.getElementById('xtream-password').value.trim();
    
    if (!url || !username || !password) {
        alert('Please enter Server URL, Username and Password');
        return;
    }
    
    document.getElementById('converter-status').textContent = 'Converting Xtream to M3U...';
    document.getElementById('converter-output').innerHTML = '<div class="checking">⏳ Converting Xtream Codes to M3U playlist...</div>';
    document.getElementById('download-btn').style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/convert/xtream-to-m3u`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentM3U = data.m3u_content;
            const output = `<div class="valid-mac">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 24px; height: 24px; color: var(--success);">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    <strong style="font-size: 1.1em;">Conversion Successful!</strong>
                </div>
                <div style="background: var(--bg-tertiary); padding: 12px; border-radius: 8px; margin: 10px 0;">
                    <div style="font-size: 0.9em; color: var(--text-secondary);">Total Channels</div>
                    <div style="font-size: 1.5em; font-weight: 700; color: var(--accent);">${data.total_channels}</div>
                </div>
                <div style="margin-top: 12px;">
                    <div style="font-weight: 600; margin-bottom: 8px;">M3U Preview (first 20 lines):</div>
                    <pre style="background: var(--bg-secondary); padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 0.85em; max-height: 300px;">${data.m3u_content.split('\n').slice(0, 20).join('\n')}${data.m3u_content.split('\n').length > 20 ? '\n...' : ''}</pre>
                </div>
            </div>`;
            document.getElementById('converter-output').innerHTML = output;
            document.getElementById('download-btn').style.display = 'inline-flex';
            document.getElementById('converter-status').textContent = `Converted ${data.total_channels} channels successfully!`;
        } else {
            document.getElementById('converter-output').innerHTML = `<div class="invalid-mac">❌ ${data.error}</div>`;
            document.getElementById('converter-status').textContent = 'Conversion failed';
        }
    } catch (error) {
        document.getElementById('converter-output').innerHTML = `<div class="invalid-mac">❌ Error: ${error.message}</div>`;
        document.getElementById('converter-status').textContent = 'Error occurred';
    }
}

async function parseM3U() {
    const m3uInput = document.getElementById('m3u-input').value.trim();
    
    if (!m3uInput) {
        alert('Please enter M3U URL or paste M3U content');
        return;
    }
    
    document.getElementById('converter-status').textContent = 'Parsing M3U...';
    document.getElementById('converter-output').innerHTML = '<div class="checking">⏳ Parsing and cleaning M3U playlist...</div>';
    document.getElementById('download-btn').style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/convert/parse-m3u`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ m3u_input: m3uInput })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentM3U = data.m3u_content;
            const output = `<div class="valid-mac">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 24px; height: 24px; color: var(--success);">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    <strong style="font-size: 1.1em;">M3U Parsed Successfully!</strong>
                </div>
                <div style="background: var(--bg-tertiary); padding: 12px; border-radius: 8px; margin: 10px 0;">
                    <div style="font-size: 0.9em; color: var(--text-secondary);">Total Channels</div>
                    <div style="font-size: 1.5em; font-weight: 700; color: var(--accent);">${data.total_channels}</div>
                </div>
                <div style="margin-top: 12px;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Cleaned M3U Preview (first 20 lines):</div>
                    <pre style="background: var(--bg-secondary); padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 0.85em; max-height: 300px;">${data.m3u_content.split('\n').slice(0, 20).join('\n')}${data.m3u_content.split('\n').length > 20 ? '\n...' : ''}</pre>
                </div>
            </div>`;
            document.getElementById('converter-output').innerHTML = output;
            document.getElementById('download-btn').style.display = 'inline-flex';
            document.getElementById('converter-status').textContent = `Parsed ${data.total_channels} channels successfully!`;
        } else {
            document.getElementById('converter-output').innerHTML = `<div class="invalid-mac">❌ ${data.error}</div>`;
            document.getElementById('converter-status').textContent = 'Parsing failed';
        }
    } catch (error) {
        document.getElementById('converter-output').innerHTML = `<div class="invalid-mac">❌ Error: ${error.message}</div>`;
        document.getElementById('converter-status').textContent = 'Error occurred';
    }
}

function downloadM3U() {
    if (!currentM3U) {
        alert('No M3U content to download');
        return;
    }
    
    const blob = new Blob([currentM3U], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `playlist_${Date.now()}.m3u`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
