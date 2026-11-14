const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const stopButton = document.getElementById("stop-button");
let activeController = null;
const chatBox = document.getElementById("chat-box");
const newChatButton = document.getElementById("new-chat-button");
const chatHistory = document.getElementById("chat-history");

let currentChatId = null;

// Display a message
function addMessage(message, className) {
    const div = document.createElement("div");
    div.classList.add("message", className);
    div.textContent = message;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}

// Clear current chat window
function clearChat() {
    chatBox.innerHTML = "";
}

// Display ChatGPT-style welcome screen
function showWelcomeScreen() {
    chatBox.innerHTML = `
        <div class="welcome-screen">
            <div class="welcome-icon">&#10022;</div>
            <h1>How can I help you today?</h1>
            <p>Ask me anything. Let's learn, create and solve problems together.</p>

            <div class="suggestion-grid">
                <div class="suggestion-card" data-prompt="Help me write a Python program.">
                    <span>&lt;/&gt;</span>
                    <strong>Write code</strong>
                    <small>Build something with Python</small>
                </div>

                <div class="suggestion-card" data-prompt="Teach me a new technical concept with examples.">
                    <span>&#9638;</span>
                    <strong>Learn something</strong>
                    <small>Understand a new concept</small>
                </div>

                <div class="suggestion-card" data-prompt="Help me improve my English writing.">
                    <span>&#9998;</span>
                    <strong>Improve writing</strong>
                    <small>Write and improve your text</small>
                </div>

                <div class="suggestion-card" data-prompt="Give me some creative project ideas for an IT student.">
                    <span>&#10023;</span>
                    <strong>Get ideas</strong>
                    <small>Explore creative possibilities</small>
                </div>
            </div>
        </div>
    `;

    chatBox.querySelectorAll(".suggestion-card").forEach(card => {
        card.addEventListener("click", () => {
            userInput.value = card.dataset.prompt;
            userInput.focus();
        });
    });
}

// Format Markdown
function formatAIResponse(element, text) {
    if (!window.marked || !window.DOMPurify) {
        element.textContent = text;
        return;
    }

    const html = marked.parse(text);
    element.innerHTML = DOMPurify.sanitize(html);

    element.querySelectorAll("pre code").forEach(code => {

        const languageClass = [...code.classList]
            .find(className => className.startsWith("language-"));

        const language = languageClass
            ? languageClass.replace("language-", "").toUpperCase()
            : "CODE";

        if (window.hljs) {
            hljs.highlightElement(code);
        }

        const header = document.createElement("div");
        header.className = "code-block-header";

        const languageLabel = document.createElement("span");
        languageLabel.textContent = language;

        const copyButton = document.createElement("button");
        copyButton.textContent = "Copy";
        copyButton.className = "copy-code-button";

        header.appendChild(languageLabel);
        header.appendChild(copyButton);

        code.parentElement.insertBefore(header, code);

        copyButton.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(code.textContent);
                copyButton.textContent = "Copied!";

                setTimeout(() => {
                    copyButton.textContent = "Copy";
                }, 1500);
            } catch {
                copyButton.textContent = "Copy failed";
            }
        });
    });
}

// Create a new chat
async function createNewChat() {
    try {
        const response = await fetch("/api/chats", {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not create chat.");
        }

        currentChatId = data.id;
        clearChat();

        showWelcomeScreen();

        await loadChatHistory();
        userInput.focus();

    } catch (error) {
        alert(error.message);
    }
}

// Load chat history sidebar
async function loadChatHistory() {
    try {
        const response = await fetch("/api/chats");

        if (!response.ok) {
            throw new Error("Could not load chat history.");
        }

        const chats = await response.json();
        chatHistory.innerHTML = "";

        if (chats.length === 0) {
            chatHistory.textContent = "No previous chats";
            return;
        }

        chats.forEach(chat => {
            const item = document.createElement("div");
            item.className = "history-item";

            const openButton = document.createElement("button");
            openButton.className = "history-chat-button";
            openButton.textContent = chat.title;
            openButton.title = chat.title;

            if (chat.id === currentChatId) {
                openButton.classList.add("selected");
            }

            openButton.addEventListener("click", () => {
                openChat(chat.id);
            });

            const deleteButton = document.createElement("button");
            deleteButton.className = "delete-chat-button";
            deleteButton.textContent = "×";
            deleteButton.title = "Delete chat";

            deleteButton.addEventListener("click", async () => {
                const confirmed = confirm("Delete this conversation?");
                if (!confirmed) return;

                await deleteChat(chat.id);
            });

            item.appendChild(openButton);
            item.appendChild(deleteButton);
            chatHistory.appendChild(item);
        });

    } catch (error) {
        chatHistory.textContent = error.message;
    }
}

// Open an existing chat
async function openChat(chatId) {
    try {
        const response = await fetch(`/api/chats/${chatId}`);
        const chat = await response.json();

        if (!response.ok) {
            throw new Error(chat.error || "Could not open chat.");
        }

        currentChatId = chatId;
        clearChat();

        if (!chat.messages || chat.messages.length === 0) {
            showWelcomeScreen();
        } else {
            chat.messages.forEach(message => {
                const messageDiv = addMessage(
                    message.content,
                    message.role === "user" ? "user-message" : "ai-message"
                );

                if (message.role === "assistant") {
                    formatAIResponse(messageDiv, message.content);
                }
            });
        }

        await loadChatHistory();

    } catch (error) {
        alert(error.message);
    }
}

// Delete a chat
async function deleteChat(chatId) {
    try {
        const response = await fetch(`/api/chats/${chatId}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            throw new Error("Could not delete chat.");
        }

        if (currentChatId === chatId) {
            currentChatId = null;
            await createNewChat();
        } else {
            await loadChatHistory();
        }

    } catch (error) {
        alert(error.message);
    }
}

// Send message and receive streaming AI response
async function sendMessage() {
    const message = userInput.value.trim();

    if (!message || sendButton.disabled) return;

    if (!currentChatId) {
        await createNewChat();
        if (!currentChatId) return;
    }

    const welcomeScreen = chatBox.querySelector(".welcome-screen");
    if (welcomeScreen) welcomeScreen.remove();

    addMessage(message, "user-message");

    userInput.value = "";
    sendButton.disabled = true;
    sendButton.textContent = "\u2191";

    const aiMessage = addMessage("", "ai-message");
    aiMessage.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    let fullResponse = "";

    const controller = new AbortController();
    activeController = controller;
    stopButton.hidden = false;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            signal: controller.signal,
            body: JSON.stringify({
                message: message,
                chat_id: currentChatId
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Request failed.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            const lines = buffer.split("\n");
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.trim()) continue;

                const data = JSON.parse(line);

                if (data.token) {
                    fullResponse += data.token;
                    aiMessage.textContent = fullResponse;
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                if (data.error) {
                    throw new Error(data.error);
                }
            }
        }

        buffer += decoder.decode();

        if (buffer.trim()) {
            const data = JSON.parse(buffer);

            if (data.token) {
                fullResponse += data.token;
            }

            if (data.error) {
                throw new Error(data.error);
            }
        }

        if (fullResponse.trim()) {
            formatAIResponse(aiMessage, fullResponse);
        } else {
            aiMessage.textContent = "No response received.";
        }

        await loadChatHistory();

    } catch (error) {
        if (error.name === "AbortError") {
            if (fullResponse.trim()) {
                formatAIResponse(aiMessage, fullResponse);
                aiMessage.append(" (Generation stopped)");
            } else {
                aiMessage.textContent = "Generation stopped.";
            }
        } else {
            aiMessage.textContent = "Error: " + error.message;
        }

    } finally {
        activeController = null;
        stopButton.hidden = true;
        sendButton.disabled = false;
        sendButton.textContent = "\u2191";
        userInput.focus();
    }
}

// Button events
newChatButton.addEventListener("click", createNewChat);
stopButton.addEventListener("click", () => {
    if (activeController) activeController.abort();
});
sendButton.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// Initialize application
async function initializeApp() {
    try {
        const response = await fetch("/api/chats");
        const chats = await response.json();

        if (chats.length > 0) {
            await openChat(chats[0].id);
        } else {
            await createNewChat();
        }
    } catch (error) {
        console.error("Initialization error:", error);
    }
}

initializeApp();



// DARK MODE
const themeToggle = document.getElementById("theme-toggle");

function applyTheme(theme) {
    document.body.classList.toggle("dark-mode", theme === "dark");

    themeToggle.textContent =
        theme === "dark" ? "Light Mode" : "Dark Mode";
}

const savedTheme = localStorage.getItem("ai-toolkit-theme") || "light";
applyTheme(savedTheme);

themeToggle.addEventListener("click", () => {
    const isDark = document.body.classList.contains("dark-mode");
    const newTheme = isDark ? "light" : "dark";

    localStorage.setItem("ai-toolkit-theme", newTheme);
    applyTheme(newTheme);
});


// EXPORT CHAT
const exportButton = document.getElementById("export-button");

async function exportChat() {
    if (!currentChatId) {
        alert("No conversation selected.");
        return;
    }

    try {
        const response = await fetch(`/api/chats/${currentChatId}`);

        if (!response.ok) {
            throw new Error("Could not retrieve conversation.");
        }

        const chat = await response.json();

        let content = "PYTHON AI TOOLKIT - CHAT EXPORT\n";
        content += "Date: " + new Date().toLocaleString() + "\n";
        content += "Title: " + chat.title + "\n";
        content += "----------------------------------------\n\n";

        chat.messages.forEach(message => {
            const role = message.role === "user" ? "You" : "AI Assistant";

            content += role + ":\n";
            content += message.content + "\n\n";
        });

        const blob = new Blob([content], {
            type: "text/plain;charset=utf-8"
        });

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = "AI_Chat_" + Date.now() + ".txt";

        document.body.appendChild(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(url);

    } catch (error) {
        alert(error.message);
    }
}

exportButton.addEventListener("click", exportChat);


// CHAT SEARCH
const chatSearch = document.getElementById("chat-search");

async function searchChats() {
    const query = chatSearch.value.trim().toLowerCase();

    try {
        const response = await fetch("/api/chats");

        if (!response.ok) {
            throw new Error("Could not search chats.");
        }

        const chats = await response.json();
        const matchingChats = [];

        for (const chat of chats) {
            const detailResponse = await fetch(`/api/chats/${chat.id}`);
            if (!detailResponse.ok) continue;

            const detail = await detailResponse.json();

            const searchableText = [
                detail.title,
                ...detail.messages.map(message => message.content)
            ].join(" ").toLowerCase();

            if (searchableText.includes(query)) {
                matchingChats.push(chat);
            }
        }

        chatHistory.innerHTML = "";

        if (matchingChats.length === 0) {
            chatHistory.textContent = "No matching chats found.";
            return;
        }

        matchingChats.forEach(chat => {
            const item = document.createElement("div");
            item.className = "history-item";

            const openButton = document.createElement("button");
            openButton.className = "history-chat-button";
            openButton.textContent = chat.title;
            openButton.title = chat.title;

            if (chat.id === currentChatId) {
                openButton.classList.add("selected");
            }

            openButton.addEventListener("click", () => openChat(chat.id));

            const deleteButton = document.createElement("button");
            deleteButton.className = "delete-chat-button";
            deleteButton.textContent = "×";
            deleteButton.title = "Delete chat";

            deleteButton.addEventListener("click", async () => {
                if (confirm("Delete this conversation?")) {
                    await deleteChat(chat.id);
                    await searchChats();
                }
            });

            item.appendChild(openButton);
            item.appendChild(deleteButton);
            chatHistory.appendChild(item);
        });

    } catch (error) {
        chatHistory.textContent = error.message;
    }
}

chatSearch.addEventListener("input", searchChats);


// CLEAR CURRENT CHAT
const clearChatButton = document.getElementById("clear-chat-button");

async function clearCurrentChat() {
    if (!currentChatId) {
        alert("Please select a conversation first.");
        return;
    }

    if (!confirm("Are you sure you want to clear all messages in this chat?")) {
        return;
    }

    try {
        const response = await fetch(
            `/api/chats/${currentChatId}/clear`,
            { method: "POST" }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Could not clear chat.");
        }

        showWelcomeScreen();

        await loadChatHistory();

        alert("Chat cleared successfully!");

    } catch (error) {
        alert(error.message);
    }
}

clearChatButton.addEventListener("click", clearCurrentChat);
