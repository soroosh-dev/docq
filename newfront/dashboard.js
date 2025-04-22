// API configuration
const DOCS_URL = SERVER_URL+'docs/';
const USERS_URL = SERVER_URL+'docs/users/search/';

// Selected documents
let selectedDocuments = new Set();
let selectedUsers = new Set();
let selectedRevokeUsers = new Set();
let currentDocumentId = null;

// Load documents into the sidebar
async function loadDocuments() {
    const documentList = document.getElementById('documentList');
    documentList.innerHTML = '';

    try {
        const response = await fetchWithAuth(DOCS_URL);
        if (!response.ok) {
            throw new Error('Failed to fetch documents');
        }
        const documents = await response.json();

        // Add a "Select All" option
        const selectAllDiv = document.createElement('div');
        selectAllDiv.className = 'list-group-item document-card mb-2';
        selectAllDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0">Select All Documents</h6>
                </div>
                <div>
                    <input type="checkbox" class="form-check-input" 
                           ${documents.length === selectedDocuments.size ? 'checked' : ''}>
                </div>
            </div>
        `;
        selectAllDiv.addEventListener('click', () => toggleAllDocuments(documents));
        documentList.appendChild(selectAllDiv);

        documents.forEach(doc => {
            const div = document.createElement('div');
            div.className = `list-group-item document-card ${selectedDocuments.has(doc.id) ? 'selected' : ''} ${doc.is_processed ? 'bg-success bg-opacity-10' : ''}`;
            div.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${doc.original_name}</h6>
                        <small class="text-muted">${doc.doc_type}</small>
                    </div>
                    <div class="text-end">
                        <input type="checkbox" class="form-check-input" ${selectedDocuments.has(doc.id) ? 'checked' : ''}>
                        <br>
                        <small class="text-muted">${new Date(doc.upload_date).toLocaleDateString()}</small>
                        ${doc.is_processed ? '<br><small class="text-success">Processed</small>' : ''}
                    </div>
                </div>
            `;
            div.addEventListener('click', (e) => {
                // Prevent checkbox from triggering the event twice
                if (e.target.type !== 'checkbox') {
                    toggleDocumentSelection(doc.id);
                }
            });
            // Handle checkbox click separately
            const checkbox = div.querySelector('input[type="checkbox"]');
            checkbox.addEventListener('change', (e) => {
                e.stopPropagation();
                toggleDocumentSelection(doc.id);
            });
            documentList.appendChild(div);
        });

        // Update selection counter and button states
        updateSelectionCounter(documents.length);
        updateActionButtons();
    } catch (error) {
        console.error('Error loading documents:', error);
        documentList.innerHTML = `
            <div class="alert alert-danger">
                Failed to load documents. Please try again later.
            </div>
        `;
    }
}

// Toggle all documents selection
function toggleAllDocuments(documents) {
    if (selectedDocuments.size === documents.length) {
        // If all documents are selected, deselect all
        selectedDocuments.clear();
    } else {
        // Otherwise, select all documents
        documents.forEach(doc => selectedDocuments.add(doc.id));
    }
    loadDocuments();
}

// Update selection counter
function updateSelectionCounter(totalDocuments) {
    const selectionInfo = document.getElementById('selectionInfo');
    if (selectionInfo) {
        selectionInfo.textContent = `${selectedDocuments.size} of ${totalDocuments} selected`;
    }
}

// Update action buttons state
function updateActionButtons() {
    const hasSelection = selectedDocuments.size > 0;
    document.getElementById('deleteBtn').disabled = !hasSelection;
    document.getElementById('grantAccessBtn').disabled = !hasSelection;
    document.getElementById('revokeAccessBtn').disabled = !hasSelection;
}

// Toggle document selection
function toggleDocumentSelection(docId) {
    if (selectedDocuments.has(docId)) {
        selectedDocuments.delete(docId);
    } else {
        selectedDocuments.add(docId);
    }
    loadDocuments();
}

// Delete selected documents
async function deleteSelectedDocuments() {
    if (selectedDocuments.size === 0) return;
    
    // Show confirmation modal
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    deleteModal.show();
}

// Confirm and execute delete
async function confirmDelete() {
    const deleteError = document.getElementById('deleteError');
    deleteError.classList.add('d-none');
    
    try {
        // Delete all selected documents
        const deletePromises = Array.from(selectedDocuments).map(docId =>
            fetchWithAuth(`${DOCS_URL}${docId}/`, {
                method: 'DELETE'
            })
        );

        const results = await Promise.allSettled(deletePromises);
        
        // Check for any failures
        const failures = results.filter(result => result.status === 'rejected');
        if (failures.length > 0) {
            throw new Error(`Failed to delete ${failures.length} documents`);
        }

        // Clear selection and reload
        selectedDocuments.clear();
        await loadDocuments();
        
        // Close modal
        const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
        deleteModal.hide();

    } catch (error) {
        console.error('Error deleting documents:', error);
        deleteError.textContent = error.message || 'Failed to delete documents. Please try again.';
        deleteError.classList.remove('d-none');
    }
}

// Upload document function
async function uploadDocument() {
    const fileInput = document.getElementById('fileInput');
    const uploadError = document.getElementById('uploadError');
    const uploadSuccess = document.getElementById('uploadSuccess');
    const file = fileInput.files[0];

    if (!file) {
        uploadError.textContent = 'Please select a file to upload';
        uploadError.classList.remove('d-none');
        return;
    }

    // Reset messages
    uploadError.classList.add('d-none');
    uploadSuccess.classList.add('d-none');

    // Create FormData
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetchWithAuth(`${DOCS_URL}upload/`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        // Show success message
        uploadSuccess.textContent = 'Document uploaded successfully!';
        uploadSuccess.classList.remove('d-none');
        
        // Reset form
        fileInput.value = '';
        
        // Reload documents list
        await loadDocuments();
        
        // Close modal after 1.5 seconds
        setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('uploadModal'));
            modal.hide();
            uploadSuccess.classList.add('d-none');
        }, 1500);

    } catch (error) {
        console.error('Error uploading document:', error);
        uploadError.textContent = 'Failed to upload document. Please try again.';
        uploadError.classList.remove('d-none');
    }
}

// Handle search form submission
document.getElementById('queryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const query = document.getElementById('queryInput').value;
    const responseContent = document.getElementById('responseContent');

    // Prepare request body
    const requestBody = {
        q: query
    };

    // Only add document_ids if documents are selected
    if (selectedDocuments.size > 0) {
        requestBody.document_ids = Array.from(selectedDocuments);
    }

    try {
        const response = await fetchWithAuth(`${DOCS_URL}query-with-response/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error('Failed to get search results');
        }

        const data = await response.json();
        
        // Display the response
        responseContent.innerHTML = `
            <div class="card mb-3">
                <div class="card-body">
                    <p class="card-text">${data.response}</p>
                </div>
            </div>
        `;

        // Display sources if available
        if (data.sources && data.sources.length > 0) {
            responseContent.innerHTML += `
                <div class="mt-4">
                    <h6>Sources:</h6>
                    ${data.sources.map(source => `
                        <div class="card mb-2">
                            <div class="card-body">
                                <h6 class="card-subtitle mb-2 text-muted">${source.document_name}</h6>
                                <p class="card-text">${source.text}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error performing search:', error);
        responseContent.innerHTML = `
            <div class="alert alert-danger">
                Failed to perform search. Please try again later.
            </div>
        `;
    }
});

// Open grant access modal
async function openGrantAccessModal() {
    if (selectedDocuments.size !== 1) {
        alert('Please select exactly one document to grant access');
        return;
    }

    currentDocumentId = Array.from(selectedDocuments)[0];
    selectedUsers.clear();
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('grantAccessModal'));
    modal.show();
    
    // Load users and current permissions
    await Promise.all([
        searchUsers(),
        loadCurrentPermissions()
    ]);
}

// Search users
async function searchUsers() {
    const searchInput = document.getElementById('userSearchInput');
    const userList = document.getElementById('userList');
    const query = searchInput.value.trim();

    try {
        const response = await fetchWithAuth(`${USERS_URL}?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }
        const users = await response.json();

        userList.innerHTML = users.map(user => `
            <tr>
                <td>
                    <input type="checkbox" class="form-check-input user-checkbox" 
                           value="${user.id}" 
                           ${selectedUsers.has(user.id) ? 'checked' : ''}>
                </td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td id="user-status-${user.id}">Loading...</td>
            </tr>
        `).join('');

        // Add event listeners to checkboxes
        document.querySelectorAll('.user-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const userId = parseInt(e.target.value);
                if (e.target.checked) {
                    selectedUsers.add(userId);
                } else {
                    selectedUsers.delete(userId);
                }
                updateSelectAllUsers();
            });
        });

        // Add event listener to select all checkbox
        document.getElementById('selectAllUsers').addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('.user-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = e.target.checked;
                const userId = parseInt(checkbox.value);
                if (e.target.checked) {
                    selectedUsers.add(userId);
                } else {
                    selectedUsers.delete(userId);
                }
            });
        });

    } catch (error) {
        console.error('Error searching users:', error);
        userList.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">
                    Failed to load users. Please try again.
                </td>
            </tr>
        `;
    }
}

// Load current permissions for the document
async function loadCurrentPermissions() {
    try {
        const response = await fetchWithAuth(`${DOCS_URL}${currentDocumentId}/permissions/`);
        if (!response.ok) {
            throw new Error('Failed to fetch permissions');
        }
        const permissions = await response.json();

        // Update user status in both tables
        permissions.forEach(permission => {
            const grantStatusCell = document.getElementById(`user-status-${permission.user.id}`);
            const revokeStatusCell = document.getElementById(`revoke-user-status-${permission.user.id}`);
            
            if (grantStatusCell) {
                grantStatusCell.innerHTML = '<span class="text-success">Has Access</span>';
            }
            if (revokeStatusCell) {
                revokeStatusCell.innerHTML = '<span class="text-success">Has Access</span>';
            }
        });
    } catch (error) {
        console.error('Error loading permissions:', error);
    }
}

// Update select all users checkbox
function updateSelectAllUsers() {
    const checkboxes = document.querySelectorAll('.user-checkbox');
    const selectAll = document.getElementById('selectAllUsers');
    selectAll.checked = checkboxes.length > 0 && Array.from(checkboxes).every(cb => cb.checked);
}

// Grant access to selected users
async function grantAccessToSelectedUsers() {
    if (selectedUsers.size === 0) {
        document.getElementById('grantAccessError').textContent = 'Please select at least one user';
        document.getElementById('grantAccessError').classList.remove('d-none');
        return;
    }

    const errorDiv = document.getElementById('grantAccessError');
    const successDiv = document.getElementById('grantAccessSuccess');
    errorDiv.classList.add('d-none');
    successDiv.classList.add('d-none');

    try {
        const grantPromises = Array.from(selectedUsers).map(userId =>
            fetchWithAuth(`${DOCS_URL}${currentDocumentId}/permissions/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId })
            })
        );

        const results = await Promise.allSettled(grantPromises);
        const failures = results.filter(result => result.status === 'rejected');
        
        if (failures.length > 0) {
            throw new Error(`Failed to grant access to ${failures.length} users`);
        }

        successDiv.textContent = 'Access granted successfully!';
        successDiv.classList.remove('d-none');
        
        // Refresh user list to show updated permissions
        await Promise.all([
            searchUsers(),
            loadCurrentPermissions()
        ]);

        // Clear selection
        selectedUsers.clear();
        document.getElementById('selectAllUsers').checked = false;

    } catch (error) {
        console.error('Error granting access:', error);
        errorDiv.textContent = error.message || 'Failed to grant access. Please try again.';
        errorDiv.classList.remove('d-none');
    }
}

// Open revoke access modal
async function openRevokeAccessModal() {
    if (selectedDocuments.size !== 1) {
        alert('Please select exactly one document to revoke access');
        return;
    }

    currentDocumentId = Array.from(selectedDocuments)[0];
    selectedRevokeUsers.clear();
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('revokeAccessModal'));
    modal.show();
    
    // Load users and current permissions
    await Promise.all([
        searchRevokeUsers(),
        loadCurrentPermissions()
    ]);
}

// Search users for revoke access
async function searchRevokeUsers() {
    const searchInput = document.getElementById('revokeUserSearchInput');
    const userList = document.getElementById('revokeUserList');
    const query = searchInput.value.trim();

    try {
        const response = await fetchWithAuth(`${USERS_URL}?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }
        const users = await response.json();

        userList.innerHTML = users.map(user => `
            <tr>
                <td>
                    <input type="checkbox" class="form-check-input revoke-user-checkbox" 
                           value="${user.id}" 
                           ${selectedRevokeUsers.has(user.id) ? 'checked' : ''}>
                </td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td id="revoke-user-status-${user.id}">Loading...</td>
            </tr>
        `).join('');

        // Add event listeners to checkboxes
        document.querySelectorAll('.revoke-user-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const userId = parseInt(e.target.value);
                if (e.target.checked) {
                    selectedRevokeUsers.add(userId);
                } else {
                    selectedRevokeUsers.delete(userId);
                }
                updateSelectAllRevokeUsers();
            });
        });

        // Add event listener to select all checkbox
        document.getElementById('selectAllRevokeUsers').addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('.revoke-user-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = e.target.checked;
                const userId = parseInt(checkbox.value);
                if (e.target.checked) {
                    selectedRevokeUsers.add(userId);
                } else {
                    selectedRevokeUsers.delete(userId);
                }
            });
        });

    } catch (error) {
        console.error('Error searching users:', error);
        userList.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">
                    Failed to load users. Please try again.
                </td>
            </tr>
        `;
    }
}

// Update select all revoke users checkbox
function updateSelectAllRevokeUsers() {
    const checkboxes = document.querySelectorAll('.revoke-user-checkbox');
    const selectAll = document.getElementById('selectAllRevokeUsers');
    selectAll.checked = checkboxes.length > 0 && Array.from(checkboxes).every(cb => cb.checked);
}

// Revoke access from selected users
async function revokeAccessFromSelectedUsers() {
    if (selectedRevokeUsers.size === 0) {
        document.getElementById('revokeAccessError').textContent = 'Please select at least one user';
        document.getElementById('revokeAccessError').classList.remove('d-none');
        return;
    }

    const errorDiv = document.getElementById('revokeAccessError');
    const successDiv = document.getElementById('revokeAccessSuccess');
    errorDiv.classList.add('d-none');
    successDiv.classList.add('d-none');

    try {
        const revokePromises = Array.from(selectedRevokeUsers).map(userId =>
            fetchWithAuth(`${DOCS_URL}${currentDocumentId}/permissions/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId })
            })
        );

        const results = await Promise.allSettled(revokePromises);
        const failures = results.filter(result => result.status === 'rejected');
        
        if (failures.length > 0) {
            throw new Error(`Failed to revoke access from ${failures.length} users`);
        }

        successDiv.textContent = 'Access revoked successfully!';
        successDiv.classList.remove('d-none');
        
        // Refresh user list to show updated permissions
        await Promise.all([
            searchRevokeUsers(),
            loadCurrentPermissions()
        ]);

        // Clear selection
        selectedRevokeUsers.clear();
        document.getElementById('selectAllRevokeUsers').checked = false;

    } catch (error) {
        console.error('Error revoking access:', error);
        errorDiv.textContent = error.message || 'Failed to revoke access. Please try again.';
        errorDiv.classList.remove('d-none');
    }
}

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();
}); 