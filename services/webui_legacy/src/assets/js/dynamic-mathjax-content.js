/**
 * @fileoverview This script dynamically loads and renders content, including MathJax equations, into a designated HTML element.
 * It supports toggling between different versions of the content (e.g., original and simplified) using a checkbox.
 * It ensures that MathJax is re-typeset whenever the content is updated.
 *
 * @author [Your Name or Your Organization's Name]
 *
 * @requires MathJax (https://www.mathjax.org/) - Make sure MathJax is included in your HTML before this script.
 *
 * Usage:
 * 1. Include this script in your HTML *after* the MathJax library.
 * 2. Create a container element (e.g., a <p> or <div>) with a unique ID.
 * 3. Add the `data-file` attribute to the container, specifying the path to the default content file.
 * 4. Create a checkbox input with the ID "toggle-simplify" to enable toggling between content versions.
 * 5. (Optional) Create a second content file (e.g., "body-simplified.md") for the simplified version.
 *
 * Example HTML:
 * <p id="content-blog-eng-1" data-file="body.md">Loading text...</p>
 * <input type="checkbox" id="toggle-simplify">
 */

// Function to fetch and insert content
function loadContent(element, simplified = false) { // Add a parameter for simplified content
            const file = simplified ? "body-simplified.md" : element.dataset.file; // Change file based on 'simplified'
            if (file) {
              fetch(file)
                .then(response => response.text())
                .then(data => {
                  element.innerHTML = data;
                  // Tell MathJax to typeset the new content
                  MathJax.typesetPromise([element])
                    .then(() => {
                      console.log("MathJax typesetting complete.");
                    })
                    .catch((err) => {
                      console.error("MathJax typesetting error:", err);
                    });
                })
                .catch(error => {
                  console.error("Error loading content:", error);
                  element.innerHTML = "Error loading content.";
                });
            }
          }

          // Load content on page load
          document.addEventListener("DOMContentLoaded", () => {
            const contentElement = document.getElementById("content-blog-eng-1");
            loadContent(contentElement);

            // Add event listener to the toggle
            const toggleSimplify = document.getElementById("toggle-simplify");
            toggleSimplify.addEventListener("change", () => {
              loadContent(contentElement, toggleSimplify.checked); // Load content based on toggle state
            });
          });
