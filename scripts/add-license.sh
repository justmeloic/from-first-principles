#!/bin/bash

# This script removes existing license headers and adds the Apache 2.0 license header to all source files.
# It logs its output to the /logs directory and must be run from the project root.

# --- Configuration ---
COPYRIGHT_HOLDER="Loïc Muhirwa"
LICENSE_TYPE="apache"
AI_SRC_DIR="services/ai/src"
WEBUI_SRC_DIR="services/webui_legacy/src"
FRONTEND_SRC_DIR="services/frontend/src"

# --- Logging Configuration ---
TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/add-license_${TIMESTAMP}.log"

# A flag to track the final outcome
OVERALL_SUCCESS=true

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages to both console and file
log() {
    echo "$1" | tee -a "$LOG_FILE"
}

# Function to remove existing license headers from JavaScript/TypeScript files
remove_js_license_headers() {
    local dir="$1"
    log "🧹 Removing existing license headers from JS/TS files in: ${dir}"

    # Find all JS/TS files and remove license headers
    find "$dir" -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) | while read -r file; do
        # Check if file starts with license header (/** ... */)
        if head -1 "$file" | grep -q "^/\*\*"; then
            # Create a temporary file with content after the license header
            temp_file=$(mktemp)

            # Use sed to remove everything from start to the first */ line, then remove leading empty lines
            sed '1,/\*\//d' "$file" | sed '/./,$!d' > "$temp_file"

            # Only replace if we have content remaining
            if [ -s "$temp_file" ]; then
                mv "$temp_file" "$file"
                log "  📝 Removed license header from: $(basename "$file")"
            else
                log "  ⚠️  Skipped $(basename "$file") - would result in empty file"
                rm -f "$temp_file"
            fi
        fi
    done
}

# Function to remove existing license headers from Python files
remove_py_license_headers() {
    local dir="$1"
    log "🧹 Removing existing license headers from Python files in: ${dir}"

    # Find all Python files and remove license headers
    find "$dir" -type f -name "*.py" | while read -r file; do
        # Check if file starts with license header (# Copyright)
        if head -1 "$file" | grep -q "^# Copyright"; then
            # Create a temporary file with content after the license header
            temp_file=$(mktemp)

            # Skip all lines starting with # until we find non-comment content, then remove leading empty lines
            sed '/^# /d; /^#$/d' "$file" | sed '/./,$!d' > "$temp_file"

            # Only replace if we have content remaining
            if [ -s "$temp_file" ]; then
                mv "$temp_file" "$file"
                log "  📝 Removed license header from: $(basename "$file")"
            else
                log "  ⚠️  Skipped $(basename "$file") - would result in empty file"
                rm -f "$temp_file"
            fi
        fi
    done
}

# --- Script Logic ---
log "🚀 Starting license application process at $(date)..."
log ""

log "🔄 Checking for 'addlicense' command..."
if ! command -v addlicense &> /dev/null; then
    log "❌ Error: 'addlicense' command not found."
    log "Please install it by running: go install github.com/google/addlicense@latest"
    exit 1 # We still exit here because the script cannot continue.
fi
log "✅ 'addlicense' is installed."
log ""

# --- Remove existing license headers ---
log "🗑️  Step 1: Removing existing license headers..."
log ""

if [ -d "$AI_SRC_DIR" ]; then
    remove_py_license_headers "$AI_SRC_DIR"
else
    log "⚠️  AI directory not found: ${AI_SRC_DIR}"
fi

if [ -d "$WEBUI_SRC_DIR" ]; then
    remove_js_license_headers "$WEBUI_SRC_DIR"
else
    log "⚠️  WebUI directory not found: ${WEBUI_SRC_DIR}"
fi

if [ -d "$FRONTEND_SRC_DIR" ]; then
    remove_js_license_headers "$FRONTEND_SRC_DIR"
else
    log "⚠️  Frontend directory not found: ${FRONTEND_SRC_DIR}"
fi
log ""

# --- Apply new license headers ---
log "📝 Step 2: Applying new license headers..."
log ""

# --- Apply license to AI Service ---
log "✍️ Applying license headers to AI service: ${AI_SRC_DIR}"
if [ -d "$AI_SRC_DIR" ]; then
    if addlicense -c "${COPYRIGHT_HOLDER}" -l "${LICENSE_TYPE}" "${AI_SRC_DIR}" >> "$LOG_FILE" 2>&1; then
        log "✅ AI service processed successfully."
    else
        log "❌ Error processing AI service. Check log for details."
        OVERALL_SUCCESS=false
    fi
else
    log "⚠️  AI service directory not found, skipping."
fi
log ""

# --- Apply license to WebUI ---
log "✍️ Applying license headers to webui: ${WEBUI_SRC_DIR}"
if [ -d "$WEBUI_SRC_DIR" ]; then
    if addlicense -c "${COPYRIGHT_HOLDER}" -l "${LICENSE_TYPE}" "${WEBUI_SRC_DIR}" >> "$LOG_FILE" 2>&1; then
        log "✅ WebUI processed successfully."
    else
        log "❌ Error processing webui. Check log for details."
        OVERALL_SUCCESS=false
    fi
else
    log "⚠️  WebUI directory not found, skipping."
fi
log ""

# --- Apply license to Frontend ---
log "✍️ Applying license headers to frontend: ${FRONTEND_SRC_DIR}"
if [ -d "$FRONTEND_SRC_DIR" ]; then
    if addlicense -c "${COPYRIGHT_HOLDER}" -l "${LICENSE_TYPE}" "${FRONTEND_SRC_DIR}" >> "$LOG_FILE" 2>&1; then
        log "✅ License headers applied to frontend successfully"
    else
        log "❌ Error processing frontend. Check log for details."
        OVERALL_SUCCESS=false
    fi
else
    log "⚠️  Frontend directory not found, skipping."
fi
log ""

# --- Final Status ---
if [ "$OVERALL_SUCCESS" = true ]; then
    log "🎉 All operations completed successfully!"
else
    log "⚠️  One or more steps failed. Please review the log."
fi

log "📋 Process log saved to: ${LOG_FILE}"

# Set the script's final exit code based on success without closing the terminal
[ "$OVERALL_SUCCESS" = true ]
