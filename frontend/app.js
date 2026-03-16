const API_BASE = window.location.origin;
const STUDENT_ID = "S001"; // Hardcoded for prototype demo

// State Variables
let currentSourceId = null;
let currentQuizData = [];
let currentQuestionIndex = 0;
let isAnswerSubmitted = false;
let currentDifficulty = "medium";

// DOM Elements
const uploadZone = document.getElementById("upload-zone");
const fileInput = document.getElementById("pdf-upload");
const uploadStatus = document.getElementById("upload-status");
const genZone = document.getElementById("generation-zone");
const btnGenerate = document.getElementById("btn-generate");
const genStatus = document.getElementById("generation-status");

const emptyState = document.getElementById("empty-state");
const quizRunner = document.getElementById("quiz-runner");
const quizComplete = document.getElementById("quiz-complete");

const qTitle = document.getElementById("question-text");
const optionsContainer = document.getElementById("options-container");
const diffBadge = document.getElementById("difficulty-badge");
const idxCurrent = document.getElementById("current-q-index");
const idxTotal = document.getElementById("total-q");

const feedbackPanel = document.getElementById("feedback-panel");
const btnNext = document.getElementById("btn-next");

// --- 1. File Upload & Ingestion Logic ---
uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadZone.classList.add("dragover");
});
uploadZone.addEventListener("dragleave", () => {
    uploadZone.classList.remove("dragover");
});
uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadZone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
        handleFileUpload(e.dataTransfer.files[0]);
    }
});
fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
        handleFileUpload(e.target.files[0]);
    }
});

async function handleFileUpload(file) {
    if (file.type !== "application/pdf") {
        uploadStatus.textContent = "Please upload a valid PDF file.";
        uploadStatus.className = "status-message status-error fade-in";
        return;
    }

    uploadStatus.textContent = `Uploading ${file.name}...`;
    uploadStatus.className = "status-message fade-in";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE}/ingest`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) throw new Error("API ingest failed");
        
        const data = await response.json();
        currentSourceId = data.source_id;
        
        uploadStatus.textContent = `Success! Parsed ${data.chunks_extracted} chunks.`;
        uploadStatus.className = "status-message status-success fade-in";
        
        // Unlock generation zone
        genZone.classList.remove("disabled");
        document.getElementById("extraction-status").textContent = `Document ID: ${currentSourceId.slice(0, 8)}... ready.`;
        
    } catch (err) {
        console.error(err);
        uploadStatus.textContent = "Failed to ingest document. Is backend running?";
        uploadStatus.className = "status-message status-error fade-in";
    }
}

// --- 2. Quiz Generation Logic ---
btnGenerate.addEventListener("click", async () => {
    if (!currentSourceId) return;

    btnGenerate.disabled = true;
    btnGenerate.innerHTML = `<i data-lucide="loader" class="pulse"></i> Analyzing Content...`;
    lucide.createIcons();

    try {
        const response = await fetch(`${API_BASE}/generate-quiz`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ source_id: currentSourceId })
        });
        
        if (!response.ok) throw new Error("Generation limits reached or failed.");
        const data = await response.json();

        genStatus.textContent = `Generated ${data.questions_generated} questions via LLM!`;
        genStatus.className = "status-message status-success fade-in";
        btnGenerate.innerHTML = `<i data-lucide="check"></i> Ready`;

        // Start local quiz session!
        startQuizSession();

    } catch (err) {
        console.error(err);
        genStatus.textContent = "Generation failed. Check console.";
        genStatus.className = "status-message status-error fade-in";
        btnGenerate.disabled = false;
        btnGenerate.innerHTML = `<i data-lucide="sparkles"></i> Try Again`;
    }
});

async function startQuizSession() {
    // Hide empty state, load questions
    emptyState.classList.add("hidden");
    
    // Fetch initial quiz list
    await fetchNextQuestionsList();
    
    if(currentQuizData.length > 0) {
        quizRunner.classList.remove("hidden");
        idxTotal.textContent = currentQuizData.length;
        renderQuestion();
    } else {
        emptyState.classList.remove("hidden");
        emptyState.querySelector("h2").textContent = "No questions found.";
    }
}

async function fetchNextQuestionsList() {
    try {
        const res = await fetch(`${API_BASE}/quiz?difficulty=${currentDifficulty}`);
        currentQuizData = await res.json();
    } catch(err) {
        console.error(err);
    }
}

// --- 3. Interactive Quiz Runner ---
function renderQuestion() {
    isAnswerSubmitted = false;
    feedbackPanel.classList.add("hidden");
    btnNext.classList.add("hidden");
    quizRunner.classList.remove("slide-in-bottom");
    // force reflow for animation restart
    void quizRunner.offsetWidth;
    quizRunner.classList.add("slide-in-bottom");

    const q = currentQuizData[currentQuestionIndex];
    
    idxCurrent.textContent = currentQuestionIndex + 1;
    qTitle.textContent = q.question;
    
    // Set Difficulty Badge UI
    diffBadge.textContent = q.difficulty;
    diffBadge.className = "difficulty-badge diff-" + q.difficulty;

    optionsContainer.innerHTML = "";
    
    if (q.type === "MCQ" || q.type === "True/False") {
        let opts = q.options;
        if (!opts || opts.length === 0) {
             // fallback just in case JSON parse failed natively
             if(q.type === 'True/False') opts = ['True', 'False']; 
             else opts = ['Option A', 'Option B'];
        }

        opts.forEach((opt, idx) => {
            const btn = document.createElement("button");
            btn.className = "option-btn fade-in";
            btn.style.animationDelay = `${idx * 0.1}s`;
            
            // Add alphabetical prefix styling A, B, C, D
            const letterMatch = String.fromCharCode(65 + idx);
            btn.innerHTML = `<strong>${letterMatch}</strong> <span>${opt}</span>`;
            
            btn.onclick = () => submitAnswer(opt, btn, q);
            optionsContainer.appendChild(btn);
        });
    } else {
        // Fill in the blank (Input field)
        const inputContainer = document.createElement("div");
        inputContainer.style.display = "flex";
        inputContainer.style.gap = "1rem";
        
        const inp = document.createElement("input");
        inp.type = "text";
        inp.placeholder = "Type your answer here...";
        inp.className = "option-btn fade-in";
        inp.style.flexGrow = "1";
        inp.style.cursor = "text";
        
        const subBtn = document.createElement("button");
        subBtn.textContent = "Submit";
        subBtn.className = "btn btn-primary";
        subBtn.onclick = () => submitAnswer(inp.value, inp, q);
        
        inputContainer.appendChild(inp);
        inputContainer.appendChild(subBtn);
        optionsContainer.appendChild(inputContainer);
    }
}

async function submitAnswer(selectedAnswer, elementClicked, questionRecord) {
    if (isAnswerSubmitted) return;
    isAnswerSubmitted = true;

    // Mark visual selection
    if (elementClicked.tagName === 'BUTTON' && !elementClicked.classList.contains('btn-primary')) {
        elementClicked.classList.add("selected");
    }

    // Call API to track adaptive difficulty
    try {
        const payload = {
            student_id: STUDENT_ID,
            question_id: questionRecord.id,
            selected_answer: selectedAnswer.toString()
        };

        const res = await fetch(`${API_BASE}/submit-answer`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        
        const apiResponse = await res.json();
        const nextDiff = apiResponse.next_recommended_difficulty;

        // Apply feedback visual style
        if (apiResponse.is_correct) {
            if (elementClicked.tagName === 'BUTTON') elementClicked.classList.add("correct");
            feedbackPanel.innerHTML = `<i data-lucide="check-circle"></i> <div>Excellent! <p>Adaptive Engine rating you higher.</p></div>`;
            feedbackPanel.className = "feedback-panel correct fade-in";
        } else {
            if (elementClicked.tagName === 'BUTTON') elementClicked.classList.add("wrong");
            feedbackPanel.innerHTML = `<i data-lucide="x-circle"></i> <div>Incorrect. <p>The correct answer was: <strong>${apiResponse.correct_answer}</strong></p></div>`;
            feedbackPanel.className = "feedback-panel wrong fade-in";
        }

        // Store recommended difficulty for next fetch
        currentDifficulty = nextDiff;
        
    } catch(err) {
        console.error(err);
    }

    lucide.createIcons();
    feedbackPanel.classList.remove("hidden");
    btnNext.classList.remove("hidden");
}

btnNext.addEventListener("click", () => {
    currentQuestionIndex++;
    if (currentQuestionIndex < currentQuizData.length) {
        renderQuestion();
    } else {
        // Quiz Exhausted
        quizRunner.classList.add("hidden");
        quizComplete.classList.remove("hidden");
    }
});
