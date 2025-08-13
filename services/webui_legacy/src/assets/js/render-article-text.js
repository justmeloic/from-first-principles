// Use the parameters object passed from the HTML
const elementId = parameters.id;
let filePath = parameters.dataFile; // Initial file path

// Find the element and toggle button
const contentElement = document.getElementById(elementId);
const toggleSimplify = document.getElementById('toggle-simplify');

// Function to fetch and parse the markdown file
function loadMarkdown(file) {
    fetch(file)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.text();
        })
        .then(text => {
            // Convert Markdown to HTML using marked.js
            const htmlContent = marked.parse(text);
            contentElement.innerHTML = htmlContent; // Inject HTML into the element
        })
        .catch(error => {
            contentElement.textContent = 'Error loading markdown file: ' + error;
        });
}

// Load the initial file (markdown)
loadMarkdown(filePath);

// Add event listener for the toggle
toggleSimplify.addEventListener('change', (event) => {
    filePath = event.target.checked ? 'body_simple.md' : 'body.md';
    loadMarkdown(filePath); // Load the selected markdown file
});
