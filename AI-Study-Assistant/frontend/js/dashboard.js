const API_URL = "http://127.0.0.1:5000/api";


const token = localStorage.getItem("access_token");
const userData = localStorage.getItem("user");


if (!token || !userData) {

    window.location.href = "index.html";

}


const user = JSON.parse(userData);


const usernameElement =
    document.getElementById("username");

const welcomeNameElement =
    document.getElementById("welcomeName");

const emailElement =
    document.getElementById("userEmail");

const initialElement =
    document.getElementById("userInitial");


if (usernameElement) {
    usernameElement.textContent = user.name;
}

if (welcomeNameElement) {
    welcomeNameElement.textContent = user.name;
}

if (emailElement) {
    emailElement.textContent = user.email;
}

if (initialElement) {
    initialElement.textContent =
        user.name.charAt(0).toUpperCase();
}

const documentFile =
    document.getElementById("documentFile");

const fileName =
    document.getElementById("fileName");


if (documentFile) {

    documentFile.addEventListener(
        "change",
        function () {

            if (this.files && this.files.length > 0) {

                fileName.textContent =
                    this.files[0].name;

            } else {

                fileName.textContent =
                    "No file selected";

            }

        }
    );

}


const uploadForm =
    document.getElementById("uploadForm");


if (uploadForm) {

    uploadForm.addEventListener(
        "submit",
        uploadDocument
    );

}


async function uploadDocument(event) {

    event.preventDefault();

    console.log("Upload button clicked");


    const file =
        documentFile.files[0];


    // No file selected
    if (!file) {

        showUploadMessage(
            "Please select a document first.",
            "error"
        );

        return;

    }


    // Check file type
    const allowedExtensions = [
        "pdf",
        "docx",
        "txt"
    ];


    const extension =
        file.name
            .split(".")
            .pop()
            .toLowerCase();


    if (!allowedExtensions.includes(extension)) {

        showUploadMessage(
            "Only PDF, DOCX and TXT files are supported.",
            "error"
        );

        return;

    }


    // Create form data
    const formData = new FormData();

    formData.append(
        "file",
        file
    );


    const button =
        document.getElementById(
            "uploadButton"
        );


    button.disabled = true;

    button.textContent =
        "Processing...";


    showUploadMessage(
        "Uploading document...",
        ""
    );


    try {

        console.log(
            "Sending document to Flask..."
        );


        const response =
            await fetch(
                `${API_URL}/documents/upload`,
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    },

                    body: formData
                }
            );


        console.log(
            "Server status:",
            response.status
        );


        const data =
            await response.json();


        console.log(
            "Server response:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Document upload failed."
            );

        }


        showUploadMessage(
            "Document uploaded successfully!",
            "success"
        );


        uploadForm.reset();


        fileName.textContent =
            "No file selected";


        await loadDocuments();


    } catch (error) {

        console.error(
            "UPLOAD ERROR:",
            error
        );


        showUploadMessage(
            error.message ||
            "Unable to upload document.",
            "error"
        );

    }


    button.disabled = false;

    button.textContent =
        "Upload Document";

}

function showUploadMessage(
    text,
    type
) {

    const message =
        document.getElementById(
            "uploadMessage"
        );


    if (!message) {
        return;
    }


    message.textContent = text;

    message.className = "message";


    if (type) {

        message.classList.add(type);

    }

}

async function loadDocuments() {

    console.log(
        "Loading documents..."
    );


    try {

        const response =
            await fetch(
                `${API_URL}/documents`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load documents."
            );

        }


        displayDocuments(
            data.documents
        );


    } catch (error) {

        console.error(
            "DOCUMENT LOAD ERROR:",
            error
        );

    }

}


function displayDocuments(
    documents
) {

    const container =
        document.getElementById(
            "documentsList"
        );


    const count =
        document.getElementById(
            "documentCount"
        );


    if (count) {

        count.textContent =
            documents.length;

    }


    if (!documents.length) {

        container.innerHTML = `

            <div class="empty-state">

                <div>📚</div>

                <h3>No documents yet</h3>

                <p>
                    Upload your first study document above.
                </p>

            </div>

        `;

        return;

    }


    container.innerHTML =
        documents.map(
            document => `

                <div class="document-card">

                    <div class="document-icon">

                        ${getFileIcon(
                            document.file_type
                        )}

                    </div>

                    <div class="document-info">

                        <h3>
                            ${escapeHtml(
                                document.filename
                            )}
                        </h3>

                        <div class="document-meta">

                            <span>
                                ${document.file_type.toUpperCase()}
                            </span>

                            <span>•</span>

                            <span class="status">
                                ${document.status}
                            </span>

                        </div>

                    </div>

                    <div class="document-action">

                        <button
                            class="chat-btn"
                            onclick="openDocument(
                                ${document.id}
                            )"
                        >
                            Chat →
                        </button>

                    </div>

                </div>

            `
        ).join("");

}


function getFileIcon(type) {

    if (type === "pdf") {
        return "📕";
    }

    if (type === "docx") {
        return "📘";
    }

    return "📄";
}


function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}

function openDocument(documentId) {

    alert(
        "Chat will be available further."
    );

}

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "user"
    );

    window.location.href =
        "index.html";

}

console.log(
    "Dashboard JavaScript loaded successfully."
);


loadDocuments();