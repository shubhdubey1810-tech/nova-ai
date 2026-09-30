// ============================================
// NØVA AI 1.0
// Multi Chat Frontend
// ============================================

const NOVA_API = "";

const messageInput =
    document.getElementById("messageInput");

const searchInput =
    document.getElementById("searchInput");

const chatContent =
    document.getElementById("chatContent");

const chat =
    document.getElementById("chat");

const conversationList =
    document.getElementById("conversationList");

let currentUser = null;

let currentConversationId = null;

let conversationMessages = [];

let deferredInstallPrompt = null;

window.addEventListener(
    "beforeinstallprompt",
    event => {
        event.preventDefault();
        deferredInstallPrompt = event;
    }
);

window.addEventListener(
    "appinstalled",
    () => {
        deferredInstallPrompt = null;
    }
);

async function installNovaPWA() {

    if (!deferredInstallPrompt) {

        window.alert(
            "NØVA AI can be installed from Chrome's Install App option."
        );

        return;
    }

    const installPrompt = deferredInstallPrompt;

    installPrompt.prompt();

    await installPrompt.userChoice;

    deferredInstallPrompt = null;
}

// ============================================
// AUTH
// ============================================

async function checkAuth() {

    try {

        const response = await fetch(
            `${NOVA_API}/auth/status`,
            {
                credentials: "include"
            }
        );

        const data =
            await response.json();

        if (
            data.authenticated &&
            data.user
        ) {

            currentUser = data.user;

            updateUserUI();

            await loadConversations();

            return true;
        }

        currentUser = null;

        updateUserUI();

        return false;

    } catch (error) {

        console.error(
            "Auth error:",
            error
        );

        currentUser = null;

        updateUserUI();

        return false;
    }
}

// ============================================
// GOOGLE LOGIN
// ============================================

function loginWithGoogle() {

    window.location.href =
        `${NOVA_API}/auth/google/login`;
}

// ============================================
// LOGOUT
// ============================================

async function logout() {

    try {

        await fetch(
            `${NOVA_API}/auth/logout`,
            {
                method: "POST",
                credentials: "include"
            }
        );

    } catch (error) {

        console.error(
            "Logout error:",
            error
        );

    } finally {

        currentUser = null;

        currentConversationId = null;

        conversationMessages = [];

        updateUserUI();

        clearChat();

        window.location.href = "/";
    }
}

// ============================================
// PROFILE UI
// ============================================

function updateUserUI() {

    const userName =
        document.getElementById(
            "userName"
        );

    const userEmail =
        document.getElementById(
            "userEmail"
        );

    const userAvatar =
        document.getElementById(
            "userAvatar"
        );

    const loginButton =
        document.getElementById(
            "loginButton"
        );

    const profileMenu =
        document.getElementById(
            "profileMenu"
        );

    if (!userName) {
        return;
    }

    if (currentUser) {

        userName.textContent =
            currentUser.name ||
            "NØVA User";

        if (userEmail) {

            userEmail.textContent =
                currentUser.email ||
                "";
        }

        if (
            userAvatar &&
            currentUser.picture
        ) {

            userAvatar.src =
                currentUser.picture;

            userAvatar.style.display =
                "block";
        }

        if (loginButton) {

            loginButton.style.display =
                "none";
        }

        if (profileMenu) {

            profileMenu.style.display =
                "flex";
        }

    } else {

        if (userName) {

            userName.textContent =
                "Not signed in";
        }

        if (userEmail) {

            userEmail.textContent =
                "";
        }

        if (userAvatar) {

            userAvatar.style.display =
                "none";
        }

        if (loginButton) {

            loginButton.style.display =
                "block";
        }

        if (profileMenu) {

            profileMenu.style.display =
                "none";
        }
    }
}

// ============================================
// LOAD CONVERSATIONS
// ============================================

async function loadConversations() {

    if (!currentUser) {
        return;
    }

    try {

        const response = await fetch(
            `${NOVA_API}/conversations`,
            {
                credentials: "include"
            }
        );

        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        renderConversationList(
            data.conversations || []
        );

        const conversations =
            data.conversations || [];

        if (!currentConversationId) {

            if (conversations.length > 0) {

                await openConversation(
                    conversations[0].id
                );

            } else {

                await createNewChat();
            }
        }

    } catch (error) {

        console.error(
            "Could not load conversations:",
            error
        );
    }
}

// ============================================
// RENDER SIDEBAR
// ============================================

function renderConversationList(
    conversations
) {

    if (!conversationList) {
        return;
    }

    conversationList.innerHTML = "";

    if (!conversations.length) {

        const empty =
            document.createElement("div");

        empty.className =
            "chat-history-empty";

        empty.textContent =
            "No chats yet.";

        conversationList.appendChild(
            empty
        );

        return;
    }

    conversations.forEach(
        conversation => {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "conversation-item";

            if (
                conversation.id ===
                currentConversationId
            ) {

                item.classList.add(
                    "active"
                );
            }

            const title =
                document.createElement(
                    "div"
                );

            title.className =
                "conversation-title";

            title.textContent =
                conversation.title ||
                "New Chat";

            const deleteButton =
                document.createElement(
                    "button"
                );

            deleteButton.className =
                "delete-conversation";

            deleteButton.textContent =
                "×";

            deleteButton.title =
                "Delete chat";

            deleteButton.addEventListener(
                "click",
                event => {

                    event.stopPropagation();

                    deleteConversation(
                        conversation.id
                    );
                }
            );

            item.appendChild(title);

            item.appendChild(
                deleteButton
            );

            item.addEventListener(
                "click",
                () => {

                    openConversation(
                        conversation.id
                    );
                }
            );

            conversationList.appendChild(
                item
            );
        }
    );
}

// ============================================
// NEW CHAT
// ============================================

async function newChat() {

    await createNewChat();
}

async function createNewChat() {

    if (!currentUser) {

        addMessage(
            "Please sign in with Google first.",
            "nova"
        );

        return;
    }

    try {

        const response =
            await fetch(
                `${NOVA_API}/conversations`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    credentials: "include",

                    body: JSON.stringify({
                        title: "New Chat"
                    })
                }
            );

        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        currentConversationId =
            data.conversation.id;

        conversationMessages = [];

        clearChat();

        await loadConversations();

        focusChat();

    } catch (error) {

        console.error(
            "Could not create chat:",
            error
        );
    }
}

// ============================================
// OPEN CHAT
// ============================================

async function openConversation(
    conversationId
) {

    if (!currentUser) {
        return;
    }

    try {

        const response =
            await fetch(
                `${NOVA_API}/conversations/${conversationId}`,
                {
                    credentials: "include"
                }
            );

        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        currentConversationId =
            data.conversation.id;

        conversationMessages =
            data.conversation.messages || [];

        renderConversation();

        await loadConversationSidebarOnly();

        focusChat();

    } catch (error) {

        console.error(
            "Could not open conversation:",
            error
        );
    }
}

// ============================================
// RENDER CURRENT CONVERSATION
// ============================================

function renderConversation() {

    clearChat();

    conversationMessages.forEach(
        item => {

            appendMessage(
                item.message,
                item.role === "user"
                    ? "user"
                    : "nova"
            );
        }
    );
}

// ============================================
// DELETE CHAT
// ============================================

async function deleteConversation(
    conversationId
) {

    if (!currentUser) {
        return;
    }

    try {

        const response =
            await fetch(
                `${NOVA_API}/conversations/${conversationId}`,
                {
                    method: "DELETE",
                    credentials: "include"
                }
            );

        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }

        if (
            conversationId ===
            currentConversationId
        ) {

            currentConversationId =
                null;

            conversationMessages = [];

            clearChat();
        }

        await loadConversations();

    } catch (error) {

        console.error(
            "Could not delete conversation:",
            error
        );
    }
}

// ============================================
// SIDEBAR REFRESH
// ============================================

async function loadConversationSidebarOnly() {

    try {

        const response =
            await fetch(
                `${NOVA_API}/conversations`,
                {
                    credentials: "include"
                }
            );

        if (!response.ok) {
            return;
        }

        const data =
            await response.json();

        renderConversationList(
            data.conversations || []
        );

    } catch (error) {

        console.error(
            "Sidebar error:",
            error
        );
    }
}

// ============================================
// SEND MESSAGE
// ============================================

async function sendMessage() {

    const userMessage =
        messageInput.value.trim();

    if (!userMessage) {
        return;
    }

    if (!currentUser) {

        addMessage(
            "Please sign in with Google before using NØVA.",
            "nova"
        );

        return;
    }

    if (!currentConversationId) {

        await createNewChat();
    }

    if (!currentConversationId) {
        return;
    }

    appendMessage(
        userMessage,
        "user"
    );

    messageInput.value = "";

    showTyping();

    try {

        const response =
            await fetch(
                `${NOVA_API}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    credentials: "include",

                    body: JSON.stringify({

                        message:
                            userMessage,

                        conversation_id:
                            currentConversationId
                    })
                }
            );

        const data =
            await response.json();

        hideTyping();

        if (
            !response.ok ||
            !data.success
        ) {

            addMessage(
                data.error ||
                data.response ||
                "NØVA could not process your request.",
                "nova"
            );

            return;
        }

        appendMessage(
            data.response,
            "nova"
        );

        await loadConversationSidebarOnly();

    } catch (error) {

        hideTyping();

        console.error(
            "NØVA chat error:",
            error
        );

        addMessage(
            "NØVA backend से connection नहीं हो पाया।",
            "nova"
        );
    }
}

// ============================================
// ADD MESSAGE
// ============================================

function appendMessage(
    text,
    type
) {

    const message =
        document.createElement("div");

    message.className =
        `message ${type}`;

    message.textContent =
        text;

    chatContent.appendChild(
        message
    );

    chat.scrollTo({
        top:
            chat.scrollHeight,

        behavior:
            "smooth"
    });
}

function addMessage(
    text,
    type
) {

    appendMessage(
        text,
        type
    );
}

// ============================================
// CLEAR CHAT
// ============================================

function clearChat() {

    chatContent.innerHTML = `
        <div class="welcome">

            <div class="nova-symbol">
                ✦
            </div>

            <h1>
                What can I help you with?
            </h1>

            <p>
                Ask NØVA anything.
            </p>

        </div>
    `;
}

// ============================================
// SEARCH
// ============================================

async function searchWeb() {

    const query =
        searchInput.value.trim();

    if (!query) {
        return;
    }

    if (!currentUser) {

        addMessage(
            "Please sign in with Google first.",
            "nova"
        );

        return;
    }

    if (!currentConversationId) {

        await createNewChat();
    }

    searchInput.value = "";

    appendMessage(
        "Search: " + query,
        "user"
    );

    showTyping();

    try {

        const response =
            await fetch(
                `${NOVA_API}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    credentials: "include",

                    body: JSON.stringify({
                        message:
                            `Search the web for: ${query}`,

                        conversation_id:
                            currentConversationId
                    })
                }
            );

        const data =
            await response.json();

        hideTyping();

        if (
            !response.ok ||
            !data.success
        ) {

            addMessage(
                data.error ||
                data.response ||
                "NØVA could not process your search.",
                "nova"
            );

            return;
        }

        appendMessage(
            data.response ||
            "No response.",
            "nova"
        );

        await loadConversationSidebarOnly();

    } catch (error) {

        hideTyping();

        console.error(
            error
        );
    }
}

// ============================================
// INPUT HELPERS
// ============================================

function searchKey(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        searchWeb();
    }
}

function messageKey(event) {

    if (event.key === "Enter") {

        if (event.shiftKey) {
            return;
        }

        event.preventDefault();

        sendMessage();
    }
}

function focusChat() {

    if (messageInput) {

        messageInput.focus();
    }
}

function focusSearch() {

    if (searchInput) {

        searchInput.focus();
    }
}

// ============================================
// MEMORY
// ============================================

function showMemory() {

    if (!currentUser) {

        addMessage(
            "Please sign in with Google first.",
            "nova"
        );

        return;
    }

    addMessage(
        "NØVA Memory will be connected to your account in the next stage.",
        "nova"
    );
}

// ============================================
// TOOLS
// ============================================

function showTools() {

    addMessage(
        "NØVA Tools will be connected in the next stage.",
        "nova"
    );
}

// ============================================
// TYPING
// ============================================

function showTyping() {

    hideTyping();

    const typing =
        document.createElement(
            "div"
        );

    typing.id =
        "novaTyping";

    typing.className =
        "message nova";

    typing.textContent =
        "NØVA is thinking...";

    chatContent.appendChild(
        typing
    );

    chat.scrollTo({
        top:
            chat.scrollHeight,

        behavior:
            "smooth"
    });
}

function hideTyping() {

    const typing =
        document.getElementById(
            "novaTyping"
        );

    if (typing) {

        typing.remove();
    }
}

// ============================================
// START
// ============================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        const authenticated =
            await checkAuth();

        if (!authenticated) {

            clearChat();

            addMessage(
                "Welcome to NØVA AI. Please sign in with Google to continue.",
                "nova"
            );

            return;
        }

        focusChat();
    }
);