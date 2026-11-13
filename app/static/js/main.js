// Enhanced Main JavaScript for Research Assistant

document.addEventListener('DOMContentLoaded', function() {
    // Handle read status toggle for papers
    const readStatusCheckboxes = document.querySelectorAll('.read-status');
    readStatusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const paperId = this.getAttribute('data-paper-id');
            const isRead = this.checked;
            updateReadStatus(paperId, isRead);
        });
    });
    
    // Handle reminder status toggle
    const reminderCheckboxes = document.querySelectorAll('.reminder-status');
    reminderCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const reminderId = this.getAttribute('data-reminder-id');
            toggleReminderStatus(reminderId);
        });
    });
    
    // Set up paper search form
    const paperSearchForm = document.getElementById('paper-search-form');
    if (paperSearchForm) {
        paperSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('paper-search-input').value.trim();
            if (query) {
                searchPapers(query);
            }
        });
    }
    
    // Set up patent search form
    const patentSearchForm = document.getElementById('patent-search-form');
    if (patentSearchForm) {
        patentSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('patent-search-input').value.trim();
            if (query) {
                searchPatents(query);
            }
        });
    }
    
    // Set up DOI fetch button
    const fetchDoiBtn = document.getElementById('fetch-doi-btn');
    if (fetchDoiBtn) {
        fetchDoiBtn.addEventListener('click', function() {
            const doi = document.getElementById('doi-input').value.trim();
            if (doi) {
                fetchDoiMetadata(doi);
            }
        });
    }
    
    // Set up citation form
    const citationForm = document.getElementById('citation-form');
    if (citationForm) {
        citationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const doi = document.getElementById('citation-doi').value.trim();
            const style = document.getElementById('citation-style').value;
            if (doi) {
                generateCitation(doi, style);
            }
        });
    }
    
    // Setup copy citation button
    const copyCitationBtn = document.getElementById('copy-citation-btn');
    if (copyCitationBtn) {
        copyCitationBtn.addEventListener('click', function() {
            const citationText = document.getElementById('citation-result').textContent;
            copyToClipboard(citationText);
        });
    }
    
    // Set date input defaults
    const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            input.value = now.toISOString().slice(0, 16);
        }
    });
    
    // Add animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});

// Update read status for a paper
function updateReadStatus(paperId, isRead) {
    // Show loading indicator
    const row = document.querySelector(`tr[data-paper-id="${paperId}"]`);
    if (row) {
        row.style.opacity = '0.7';
    }
    
    fetch(`/papers/${paperId}/toggle-read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ read_status: isRead }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            if (row) {
                row.style.opacity = '1';
                if (isRead) {
                    row.classList.add('table-success');
                } else {
                    row.classList.remove('table-success');
                }
            }
        } else {
            console.error('Error updating read status:', data.message);
            // Revert checkbox state
            const checkbox = document.querySelector(`input[data-paper-id="${paperId}"]`);
            if (checkbox) {
                checkbox.checked = !isRead;
            }
        }
    })
    .catch(error => {
        console.error('Error updating read status:', error);
        // Revert checkbox state
        const checkbox = document.querySelector(`input[data-paper-id="${paperId}"]`);
        if (checkbox) {
            checkbox.checked = !isRead;
        }
        if (row) {
            row.style.opacity = '1';
        }
    });
}

// Toggle reminder status
function toggleReminderStatus(reminderId) {
    const reminderItem = document.querySelector(`li[data-reminder-id="${reminderId}"]`);
    const checkbox = document.querySelector(`input[data-reminder-id="${reminderId}"]`);
    
    if (reminderItem) {
        reminderItem.style.opacity = '0.7';
    }
    
    fetch(`/reminders/${reminderId}/toggle`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            if (reminderItem) {
                reminderItem.style.opacity = '1';
                const reminderText = reminderItem.querySelector('.reminder-text');
                
                if (data.completed) {
                    reminderItem.classList.add('text-muted');
                    if (reminderText) {
                        reminderText.style.textDecoration = 'line-through';
                    }
                } else {
                    reminderItem.classList.remove('text-muted');
                    if (reminderText) {
                        reminderText.style.textDecoration = 'none';
                    }
                }
            }
        } else {
            console.error('Error toggling reminder:', data.message);
            // Revert checkbox state
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
            }
        }
    })
    .catch(error => {
        console.error('Error toggling reminder:', error);
        // Revert checkbox state
        if (checkbox) {
            checkbox.checked = !checkbox.checked;
        }
        if (reminderItem) {
            reminderItem.style.opacity = '1';
        }
    });
}

// Fetch DOI metadata
function fetchDoiMetadata(doi) {
    // Show loading indicator
    const doiInput = document.getElementById('doi-input');
    const fetchDoiBtn = document.getElementById('fetch-doi-btn');
    
    if (doiInput) {
        doiInput.disabled = true;
    }
    if (fetchDoiBtn) {
        fetchDoiBtn.disabled = true;
        fetchDoiBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    }
    
    fetch(`/papers/doi/${encodeURIComponent(doi)}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Error fetching DOI metadata:', data.error);
            alert(`Error: ${data.error}`);
        } else {
            fillPaperForm(data);
        }
    })
    .catch(error => {
        console.error('Error fetching DOI metadata:', error);
        alert('Error fetching DOI metadata. Please try again or enter details manually.');
    })
    .finally(() => {
        if (doiInput) {
            doiInput.disabled = false;
        }
        if (fetchDoiBtn) {
            fetchDoiBtn.disabled = false;
            fetchDoiBtn.innerHTML = '<i class="fas fa-cloud-download-alt"></i>';
        }
    });
}

// Search for papers
function searchPapers(query) {
    const resultsContainer = document.getElementById('paper-search-results');
    
    if (resultsContainer) {
        // Show loading indicator
        resultsContainer.innerHTML = `
            <div class="d-flex justify-content-center my-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        fetch(`/papers/search?query=${encodeURIComponent(query)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="alert alert-info">
                        No papers found matching "${query}". Try a different search term.
                    </div>
                `;
            } else {
                let html = `<p class="mb-3">Found ${data.length} papers matching "${query}":</p>`;
                html += '<div class="list-group">';
                
                data.forEach(paper => {
                    const authors = paper.authors || 'Unknown authors';
                    const year = paper.year || 'N/A';
                    const publication = paper.publication || 'Unknown publication';
                    
                    html += `
                        <div class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between mb-1">
                                <h6 class="mb-1">${paper.title}</h6>
                                <small>${year}</small>
                            </div>
                            <p class="mb-1 small">${authors}</p>
                            <p class="mb-1 small text-muted">${publication}</p>
                            <div class="d-flex justify-content-between align-items-center mt-2">
                                <small class="text-muted">${paper.doi || 'No DOI available'}</small>
                                <button class="btn btn-sm btn-primary" 
                                    onclick="fillPaperForm({
                                        title: '${paper.title.replace(/'/g, "\\'")}', 
                                        authors: '${paper.authors ? paper.authors.replace(/'/g, "\\'") : ""}', 
                                        publication: '${paper.publication ? paper.publication.replace(/'/g, "\\'") : ""}', 
                                        year: '${paper.year || ""}', 
                                        doi: '${paper.doi || ""}', 
                                        url: '${paper.url || ""}'
                                    })">
                                    <i class="fas fa-plus-circle me-1"></i> Add
                                </button>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                resultsContainer.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Error searching papers:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error searching papers. Please try again later.
                </div>
            `;
        });
    }
}

// Fill paper form with data
function fillPaperForm(paperData) {
    document.getElementById('title').value = paperData.title || '';
    document.getElementById('authors').value = paperData.authors || '';
    document.getElementById('publication').value = paperData.publication || '';
    document.getElementById('year').value = paperData.year || '';
    document.getElementById('doi').value = paperData.doi || '';
    document.getElementById('url').value = paperData.url || '';
    document.getElementById('abstract').value = paperData.abstract || '';
    document.getElementById('keywords').value = paperData.keywords || '';
    
    // Collapse search section and show add paper form
    const searchCollapse = bootstrap.Collapse.getInstance(document.getElementById('searchPaperCollapse'));
    if (searchCollapse) {
        searchCollapse.hide();
    }
    
    const addCollapse = document.getElementById('addPaperCollapse');
    if (addCollapse) {
        const bsCollapse = new bootstrap.Collapse(addCollapse, {
            show: true
        });
    }
    
    // Highlight the form with a subtle animation
    const form = document.querySelector('form[action="/papers/add"]');
    if (form) {
        form.style.animation = 'none';
        setTimeout(() => {
            form.style.animation = 'fadeIn 0.5s ease-out';
        }, 10);
    }
}

// Search for patents
function searchPatents(query) {
    const resultsContainer = document.getElementById('patent-search-results');
    
    if (resultsContainer) {
        // Show loading indicator
        resultsContainer.innerHTML = `
            <div class="d-flex justify-content-center my-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        fetch(`/patents/search?query=${encodeURIComponent(query)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="alert alert-info">
                        No patents found matching "${query}". Try a different search term.
                    </div>
                `;
            } else {
                let html = `<p class="mb-3">Found ${data.length} patents matching "${query}":</p>`;
                html += '<div class="list-group">';
                
                data.forEach(patent => {
                    const inventors = patent.inventors || 'Unknown inventors';
                    const assignee = patent.assignee || 'Unknown assignee';
                    
                    html += `
                        <div class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between mb-1">
                                <h6 class="mb-1">${patent.title}</h6>
                                <small>${patent.patent_number || 'N/A'}</small>
                            </div>
                            <p class="mb-1 small">Inventors: ${inventors}</p>
                            <p class="mb-1 small text-muted">Assignee: ${assignee}</p>
                            <div class="d-flex justify-content-between align-items-center mt-2">
                                <small class="text-muted">${patent.date || 'No date available'}</small>
                                <button class="btn btn-sm btn-primary" 
                                    onclick="fillPatentForm({
                                        title: '${patent.title.replace(/'/g, "\\'")}', 
                                        patent_number: '${patent.patent_number || ""}', 
                                        inventors: '${patent.inventors ? patent.inventors.replace(/'/g, "\\'") : ""}', 
                                        assignee: '${patent.assignee ? patent.assignee.replace(/'/g, "\\'") : ""}', 
                                        url: '${patent.url || ""}',
                                        abstract: '${patent.abstract ? patent.abstract.replace(/'/g, "\\'").replace(/\\n/g, "\\\\n") : ""}'
                                    })">
                                    <i class="fas fa-plus-circle me-1"></i> Add
                                </button>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                resultsContainer.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Error searching patents:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error searching patents. Please try again later.
                </div>
            `;
        });
    }
}

// Fill patent form with data
function fillPatentForm(patentData) {
    document.getElementById('title').value = patentData.title || '';
    document.getElementById('patent_number').value = patentData.patent_number || '';
    document.getElementById('inventors').value = patentData.inventors || '';
    document.getElementById('assignee').value = patentData.assignee || '';
    document.getElementById('url').value = patentData.url || '';
    document.getElementById('abstract').value = patentData.abstract || '';
    
    // Collapse search section and show add patent form
    const searchCollapse = bootstrap.Collapse.getInstance(document.getElementById('searchPatentCollapse'));
    if (searchCollapse) {
        searchCollapse.hide();
    }
    
    const addCollapse = document.getElementById('addPatentCollapse');
    if (addCollapse) {
        const bsCollapse = new bootstrap.Collapse(addCollapse, {
            show: true
        });
    }
}

// Generate citation
function generateCitation(doi, style) {
    const citationResult = document.getElementById('citation-result');
    const copyBtn = document.getElementById('copy-citation-btn');
    
    if (citationResult) {
        // Show loading state
        citationResult.classList.remove('d-none');
        citationResult.innerHTML = `
            <div class="d-flex justify-content-center my-2">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span class="ms-2">Generating citation...</span>
            </div>
        `;
        
        fetch('/papers/citation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ doi, style }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            citationResult.textContent = data.citation;
            
            if (copyBtn) {
                copyBtn.classList.remove('d-none');
            }
        })
        .catch(error => {
            console.error('Error generating citation:', error);
            citationResult.innerHTML = `
                <div class="text-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error generating citation. Please check the DOI and try again.
                </div>
            `;
            
            if (copyBtn) {
                copyBtn.classList.add('d-none');
            }
        });
    }
}

// Copy text to clipboard
function copyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    
    // Show a toast or alert
    const copyBtn = document.getElementById('copy-citation-btn');
    if (copyBtn) {
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
        copyBtn.classList.remove('btn-outline-secondary');
        copyBtn.classList.add('btn-success');
        
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.classList.remove('btn-success');
            copyBtn.classList.add('btn-outline-secondary');
        }, 1500);
    }
}

// Function to confirm delete actions
function confirmDelete(type, id, name) {
    if (confirm(`Are you sure you want to delete ${name}? This action cannot be undone.`)) {
        document.getElementById(`delete-${type}-${id}`).submit();
    }
}