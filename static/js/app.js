let totalScans = 0;
let uniqueUsers = new Set();
let todayScans = 0;
const today = new Date().toDateString();

// Load existing logs from database on page load
async function loadExistingLogs() {
    try {
        const response = await fetch('/api/logs?limit=50');
        const data = await response.json();
        
        if (data.logs && data.logs.length > 0) {
            // Process existing logs in reverse order (oldest first for display)
            const reversedLogs = [...data.logs].reverse();
            reversedLogs.forEach(log => {
                addLogRow(log);
                uniqueUsers.add(log.user);
                
                const logDate = new Date(log.time).toDateString();
                if (logDate === today) {
                    todayScans++;
                }
            });
            
            totalScans = data.logs.length;
            updateStats();
        }
    } catch (error) {
        console.error('Failed to load existing logs:', error);
    }
}

function updateStats() {
    document.getElementById('totalScans').textContent = totalScans;
    document.getElementById('uniqueUsers').textContent = uniqueUsers.size;
    document.getElementById('todayScans').textContent = todayScans;
}

function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    toastMessage.textContent = message;
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

function addLogRow(log) {
    const tbody = document.getElementById('logTableBody');
    const row = document.createElement('tr');
    
    row.innerHTML = `
        <td class="time">${log.time}</td>
        <td><span class="uid">${log.uid}</span></td>
        <td class="user">${log.user}</td>
    `;
    
    tbody.insertBefore(row, tbody.firstChild);
    
    // Keep only last 50 rows for performance
    if (tbody.children.length > 50) {
        tbody.removeChild(tbody.lastChild);
    }
}

// Initialize SocketIO connection
var socket = io();

socket.on("new_log", function(log) {
    totalScans++;
    uniqueUsers.add(log.user);
    
    const logDate = new Date(log.time).toDateString();
    if (logDate === today) {
        todayScans++;
    }
    
    updateStats();
    addLogRow(log);
    
    // Show notification
    showToast(`${log.user} scanned card ${log.uid}`);
});

// Load existing logs when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadExistingLogs();
});

// Initialize stats
updateStats(); 