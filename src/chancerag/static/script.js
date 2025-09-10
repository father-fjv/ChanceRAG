// DOM Elements
const chatText = document.getElementById('chatText');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const typingIndicator = document.getElementById('typingIndicator');
const menuButton = document.getElementById('menuButton');
const closeButton = document.getElementById('closeButton');
const menu = document.querySelector('.kn-llm-menu');
const switchMode = document.getElementById('switchMode');

// Settings Modal Elements
const settingsModal = document.getElementById('settingsModal');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModalClose = document.getElementById('settingsModalClose');
const topKSlider = document.getElementById('topK');
const scoreThresholdSlider = document.getElementById('scoreThreshold');
const includeSourcesCheckbox = document.getElementById('includeSources');
const topKValue = document.getElementById('topKValue');
const scoreThresholdValue = document.getElementById('scoreThresholdValue');
const saveSettingsBtn = document.getElementById('saveSettings');

// Stats Modal Elements
const statsModal = document.getElementById('statsModal');
const statsBtn = document.getElementById('statsBtn');
const statsModalClose = document.getElementById('statsModalClose');
const statsContent = document.getElementById('statsContent');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadFAQQuestions();
    initializeSettings();
});

function initializeEventListeners() {
    // Message input
    chatText.addEventListener('keydown', handleKeyDown);
    chatText.addEventListener('input', autoResize);
    sendButton.addEventListener('click', sendMessage);

    // Menu toggle
    menuButton.addEventListener('click', toggleMenu);
    closeButton.addEventListener('click', closeMenu);
    
    // Dark mode toggle
    switchMode.addEventListener('change', toggleDarkMode);
    
    // Modal events
    if (settingsModal) {
        settingsModal.addEventListener('click', function(e) {
            if (e.target === settingsModal) {
                closeModal(settingsModal);
            }
        });
    }
    
    if (statsModal) {
        statsModal.addEventListener('click', function(e) {
            if (e.target === statsModal) {
                closeModal(statsModal);
            }
        });
    }
    
    // Settings
    if (topKSlider) {
        topKSlider.addEventListener('input', updateThresholdValue);
    }
    if (scoreThresholdSlider) {
        scoreThresholdSlider.addEventListener('input', updateThresholdValue);
    }
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }
}

function initializeSettings() {
    // Load saved settings
    const savedTopK = localStorage.getItem('topK') || '3';
    const savedScoreThreshold = localStorage.getItem('scoreThreshold') || '0.3';
    const savedIncludeSources = localStorage.getItem('includeSources') !== 'false';
    
    if (topKSlider) {
        topKSlider.value = savedTopK;
        topKValue.textContent = savedTopK;
    }
    if (scoreThresholdSlider) {
        scoreThresholdSlider.value = savedScoreThreshold;
        scoreThresholdValue.textContent = savedScoreThreshold;
    }
    if (includeSourcesCheckbox) {
        includeSourcesCheckbox.checked = savedIncludeSources;
    }
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function autoResize() {
    chatText.style.height = 'auto';
    chatText.style.height = Math.min(chatText.scrollHeight, 120) + 'px';
    
    // Enable/disable send button
    sendButton.disabled = !chatText.value.trim();
}

function sendMessage() {
    const message = chatText.value.trim();
    if (!message) return;
    
    // Add user message
    addMessage(message, 'user');
    
    // Clear input
    chatText.value = '';
    autoResize();
    
    // Hide FAQ questions after first message
    const faqGrid = document.getElementById('faqGrid');
    if (faqGrid && faqGrid.style.display !== 'none') {
        faqGrid.style.display = 'none';
    }
    
    // Send query
    sendQuery(message);
}

function addMessage(text, sender) {
    const messageId = 'msg_' + Date.now();
    const messageElement = createMessageContainer(text, sender, messageId);
    chatMessages.appendChild(messageElement);
    scrollToBottom();
    return messageElement;
}

function createMessageContainer(text, sender, messageId) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.id = messageId;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'user' ? '<i class="bi bi-person"></i>' : '<i class="bi bi-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = text;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('ko-KR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    content.appendChild(textDiv);
    content.appendChild(timeDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    return messageDiv;
}

async function sendQuery(question) {
    showTypingIndicator();
    
    try {
        const requestBody = {
            question: question,
            top_k: parseInt(topKSlider?.value || '3'),
            score_threshold: parseFloat(scoreThresholdSlider?.value || '0.3'),
            include_sources: includeSourcesCheckbox?.checked !== false
        };
        
        // Try streaming first
        const streamingSupported = await testStreamingSupport();
        if (streamingSupported) {
            await sendStreamingQuery(requestBody);
        } else {
            await sendRegularQuery(requestBody);
        }
        
    } catch (error) {
        console.error('Error sending query:', error);
        hideTypingIndicator();
        addMessage('죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.', 'bot');
    }
}

async function testStreamingSupport() {
    // Always use regular query since streaming is disabled
    return false;
}

async function sendStreamingQuery(requestBody) {
    try {
        const response = await fetch('/api/v1/query/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        // Add bot message container
        const botMessage = addMessage('', 'bot');
        const messageContent = botMessage.querySelector('.message-text');
        const sources = [];
        
        hideTypingIndicator();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        // Add sources if available
                        if (sources && sources.length > 0) {
                            addSourcesToMessage(messageContent, sources);
                        }
                        
                        // Load and display related questions
                        loadRelatedQuestions(requestBody.question).then(relatedQuestions => {
                            displayRelatedQuestions(relatedQuestions, messageContent);
                        });
                        
                        return;
                    }
                    
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.type === 'token') {
                            messageContent.textContent += parsed.content;
                            scrollToBottom();
                        } else if (parsed.type === 'sources' && parsed.sources) {
                            sources.push(...parsed.sources);
                        }
                    } catch (e) {
                        // Ignore parsing errors for incomplete chunks
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Streaming error:', error);
        hideTypingIndicator();
        addMessage('스트리밍 중 오류가 발생했습니다. 일반 모드로 전환합니다.', 'bot');
        await sendRegularQuery(requestBody);
    }
}

async function sendRegularQuery(requestBody) {
    try {
        const response = await fetch('/api/v1/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        hideTypingIndicator();
        
        // Add bot response
        const botMessage = addMessage(data.answer, 'bot');
        
        // Add sources if available
        if (data.sources && data.sources.length > 0) {
            const messageContent = botMessage.querySelector('.message-text');
            addSourcesToMessage(messageContent, data.sources);
        }
        
        // Add processing time info
        if (data.processing_time) {
            const messageTime = botMessage.querySelector('.message-time');
            messageTime.textContent += ` (${data.processing_time.toFixed(2)}초)`;
        }
        
        // Load and display related questions
        const messageContent = botMessage.querySelector('.message-text');
        loadRelatedQuestions(requestBody.question).then(relatedQuestions => {
            displayRelatedQuestions(relatedQuestions, messageContent);
        });
        
    } catch (error) {
        console.error('Query error:', error);
        hideTypingIndicator();
        addMessage('죄송합니다. 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.', 'bot');
    }
}

function showTypingIndicator() {
    typingIndicator.style.display = 'block';
    scrollToBottom();
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addSourcesToMessage(messageElement, sources) {
    const sourcesDiv = document.createElement('div');
    sourcesDiv.className = 'sources';
    
    const title = document.createElement('h4');
    title.innerHTML = '<i class="bi bi-file-text"></i> 참고 문서';
    sourcesDiv.appendChild(title);
    
    sources.forEach(source => {
        const sourceItem = document.createElement('div');
        sourceItem.className = 'source-item';
        
        const sourceTitle = document.createElement('strong');
        sourceTitle.textContent = source.metadata?.source || '알 수 없는 문서';
        
        const sourceContent = document.createElement('div');
        sourceContent.className = 'source-content';
        sourceContent.textContent = source.page_content?.substring(0, 200) + '...';
        
        const sourceScore = document.createElement('div');
        sourceScore.className = 'source-score';
        sourceScore.textContent = `유사도: ${(source.score * 100).toFixed(1)}%`;
        
        sourceItem.appendChild(sourceTitle);
        sourceItem.appendChild(sourceContent);
        sourceItem.appendChild(sourceScore);
        sourcesDiv.appendChild(sourceItem);
    });
    
    messageElement.appendChild(sourcesDiv);
}

// FAQ Questions functions
async function loadFAQQuestions() {
    try {
        const response = await fetch('/api/v1/faq/questions?count=5');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayFAQQuestions(data.questions);
        
    } catch (error) {
        console.error('Error loading FAQ questions:', error);
        // Hide FAQ section if error
        const faqGrid = document.getElementById('faqGrid');
        if (faqGrid) {
            faqGrid.style.display = 'none';
        }
    }
}

function displayFAQQuestions(questions) {
    const faqGrid = document.getElementById('faqGrid');
    if (!faqGrid) return;
    
    faqGrid.innerHTML = '';
    
    questions.forEach(question => {
        const questionDiv = document.createElement('div');
        questionDiv.innerHTML = `
            <div>${question}</div>
            <div>+</div>
        `;
        
        questionDiv.addEventListener('click', () => {
            chatText.value = question;
            autoResize();
            sendMessage();
        });
        
        faqGrid.appendChild(questionDiv);
    });
}

async function loadRelatedQuestions(currentQuestion) {
    try {
        const requestBody = {
            question: currentQuestion,
            top_k: 3,
            score_threshold: 0.3,
            include_sources: false
        };
        
        const response = await fetch('/api/v1/faq/related', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.related_questions || [];
        
    } catch (error) {
        console.error('Error loading related questions:', error);
        return [];
    }
}

function displayRelatedQuestions(questions, messageElement) {
    if (!questions || questions.length === 0) return;
    
    const relatedDiv = document.createElement('div');
    relatedDiv.className = 'related-questions';
    
    const title = document.createElement('h4');
    title.innerHTML = '<i class="bi bi-lightbulb"></i> 관련 질문';
    relatedDiv.appendChild(title);
    
    questions.forEach(question => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'related-question';
        questionDiv.textContent = question;
        
        questionDiv.addEventListener('click', () => {
            chatText.value = question;
            autoResize();
            sendMessage();
        });
        
        relatedDiv.appendChild(questionDiv);
    });
    
    messageElement.appendChild(relatedDiv);
}

// Menu functions
function toggleMenu() {
    menu.classList.toggle('show');
}

function closeMenu() {
    menu.classList.remove('show');
}

// Dark mode functions
function toggleDarkMode() {
    const body = document.body;
    const isDark = switchMode.checked;
    
    if (isDark) {
        body.setAttribute('data-bs-theme', 'dark');
        localStorage.setItem('darkMode', 'true');
    } else {
        body.setAttribute('data-bs-theme', 'light');
        localStorage.setItem('darkMode', 'false');
    }
}

// Load dark mode preference
function loadDarkModePreference() {
    const savedMode = localStorage.getItem('darkMode');
    if (savedMode === 'true') {
        switchMode.checked = true;
        document.body.setAttribute('data-bs-theme', 'dark');
    }
}

// Settings functions
function updateThresholdValue() {
    if (topKValue && topKSlider) {
        topKValue.textContent = topKSlider.value;
    }
    if (scoreThresholdValue && scoreThresholdSlider) {
        scoreThresholdValue.textContent = scoreThresholdSlider.value;
    }
}

function saveSettings() {
    if (topKSlider) {
        localStorage.setItem('topK', topKSlider.value);
    }
    if (scoreThresholdSlider) {
        localStorage.setItem('scoreThreshold', scoreThresholdSlider.value);
    }
    if (includeSourcesCheckbox) {
        localStorage.setItem('includeSources', includeSourcesCheckbox.checked);
    }
    
    closeModal(settingsModal);
    
    // Show success message
    const successMessage = document.createElement('div');
    successMessage.className = 'alert alert-success';
    successMessage.textContent = '설정이 저장되었습니다.';
    successMessage.style.position = 'fixed';
    successMessage.style.top = '20px';
    successMessage.style.right = '20px';
    successMessage.style.zIndex = '3000';
    successMessage.style.padding = '1rem';
    successMessage.style.borderRadius = '6px';
    successMessage.style.backgroundColor = '#d4edda';
    successMessage.style.color = '#155724';
    successMessage.style.border = '1px solid #c3e6cb';
    
    document.body.appendChild(successMessage);
    
    setTimeout(() => {
        successMessage.remove();
    }, 3000);
}

// Modal functions
function openModal(modal) {
    modal.classList.add('show');
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal(modal) {
    modal.classList.remove('show');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Stats functions
async function loadStats() {
    try {
        const response = await fetch('/api/v1/stats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayStats(data);
        
    } catch (error) {
        console.error('Error loading stats:', error);
        statsContent.innerHTML = '<div class="alert alert-danger">통계를 불러올 수 없습니다.</div>';
    }
}

function displayStats(stats) {
    statsContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">벡터 저장소</h6>
                    </div>
                    <div class="card-body">
                        <p class="mb-1"><strong>문서 수:</strong> ${stats.vector_store?.document_count || 0}</p>
                        <p class="mb-1"><strong>임베딩 모델:</strong> ${stats.vector_store?.embedding_model || 'N/A'}</p>
                        <p class="mb-0"><strong>차원:</strong> ${stats.vector_store?.dimension || 'N/A'}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">검색기</h6>
                    </div>
                    <div class="card-body">
                        <p class="mb-1"><strong>검색 횟수:</strong> ${stats.retriever?.search_count || 0}</p>
                        <p class="mb-1"><strong>평균 검색 시간:</strong> ${stats.retriever?.avg_search_time?.toFixed(3) || 0}초</p>
                        <p class="mb-0"><strong>상태:</strong> ${stats.retriever?.status || 'N/A'}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">생성기</h6>
                    </div>
                    <div class="card-body">
                        <p class="mb-1"><strong>생성 횟수:</strong> ${stats.generator?.generation_count || 0}</p>
                        <p class="mb-1"><strong>평균 생성 시간:</strong> ${stats.generator?.avg_generation_time?.toFixed(3) || 0}초</p>
                        <p class="mb-0"><strong>모델:</strong> ${stats.generator?.model || 'N/A'}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">시스템</h6>
                    </div>
                    <div class="card-body">
                        <p class="mb-1"><strong>상태:</strong> ${stats.system_status || 'N/A'}</p>
                        <p class="mb-1"><strong>업타임:</strong> ${stats.uptime || 'N/A'}</p>
                        <p class="mb-0"><strong>버전:</strong> ${stats.version || 'N/A'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Initialize dark mode on load
loadDarkModePreference();

// Auto-resize textarea on load
autoResize();