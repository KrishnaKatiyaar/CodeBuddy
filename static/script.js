document.addEventListener('DOMContentLoaded', () => {
    // Core Code Analysis Functionality
    const analyzeButton = document.getElementById('analyzeButton');
    const analysisOutput = document.getElementById('analysisOutput');
    const languageSelect = document.getElementById('languageSelect');
    const formatCode = document.getElementById('formatCode');
    const shareCode = document.getElementById('shareCode');
    const settings = document.getElementById('settings');

    if (analyzeButton && analysisOutput) {
        analyzeButton.addEventListener('click', async function() {
            const code = window.editor.getValue();
            const language = languageSelect.value;
            
            if (!code) {
                analysisOutput.innerHTML = `
                    <div class="text-center py-12">
                        <div class="text-red-400 font-semibold">Please enter some code to analyze</div>
                    </div>
                `;
                return;
            }

            // Show loading state
            analysisOutput.innerHTML = `
                <div class="text-center py-12">
                    <div class="animate-spin w-12 h-12 mx-auto text-blue-500 mb-4">
                        <svg class="w-full h-full" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                        </svg>
                    </div>
                    <div class="text-lg font-semibold text-gray-400">Analyzing Code...</div>
                </div>
            `;
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code, language })
                });

                const data = await response.json();
                
                if (data.error) {
                    analysisOutput.innerHTML = `
                        <div class="analysis-card">
                            <div class="analysis-card-header text-red-400">Error</div>
                            <div class="analysis-card-content">${data.error}</div>
                        </div>
                    `;
                    return;
                }

                // Display results
                let resultsHtml = '<div class="space-y-4">';

                // Summary section
                resultsHtml += `
                    <div class="analysis-card">
                        <div class="analysis-card-header">
                            Analysis Summary
                        </div>
                        <div class="analysis-card-content">
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <div class="text-sm text-gray-400">Memory Leaks</div>
                                    <div class="text-xl text-red-400">${data.memory_leaks?.length || 0}</div>
                                </div>
                                <div>
                                    <div class="text-sm text-gray-400">Code Issues</div>
                                    <div class="text-xl text-yellow-400">${data.code_analysis?.length || 0}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // Memory Leaks
                if (data.memory_leaks?.length > 0) {
                    resultsHtml += `
                        <div class="analysis-card">
                            <div class="analysis-card-header text-red-400">
                                Memory Leaks
                            </div>
                            <div class="analysis-card-content space-y-4">
                                ${data.memory_leaks.map(issue => `
                                    <div class="p-3 bg-red-500/5 border border-red-500/20 rounded">
                                        <div class="flex justify-between">
                                            <span class="text-red-400">Line ${issue.line}</span>
                                            <span class="text-red-400">${issue.severity}</span>
                                        </div>
                                        <div class="mt-2 text-gray-300">${issue.issue}</div>
                                        <div class="mt-1 text-sm text-green-400">Fix: ${issue.fix}</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }

                // Code Analysis
                if (data.code_analysis?.length > 0) {
                    resultsHtml += `
                        <div class="analysis-card">
                            <div class="analysis-card-header text-yellow-400">
                                Code Analysis
                            </div>
                            <div class="analysis-card-content space-y-4">
                                ${data.code_analysis.map(issue => `
                                    <div class="p-3 bg-yellow-500/5 border border-yellow-500/20 rounded">
                                        <div class="flex justify-between">
                                            <span class="text-yellow-400">${issue.type}</span>
                                            <span class="text-yellow-400">Line ${issue.line}</span>
                                        </div>
                                        <div class="mt-2 text-gray-300">${issue.suggestion}</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }

                // AI Analysis
                if (data.ai_analysis?.length > 0) {
                    resultsHtml += `
                        <div class="analysis-card">
                            <div class="analysis-card-header text-blue-400">
                                AI Analysis
                            </div>
                            <div class="analysis-card-content space-y-4">
                                ${data.ai_analysis.map(issue => `
                                    <div class="p-3 bg-blue-500/5 border border-blue-500/20 rounded">
                                        <div class="flex justify-between">
                                            <span class="text-blue-400">${issue.type}</span>
                                            <span class="text-blue-400">${Math.round(issue.confidence * 100)}% confidence</span>
                                        </div>
                                        <div class="mt-2 text-gray-300">${issue.issue}</div>
                                        <div class="mt-1 text-sm text-green-400">Suggestion: ${issue.suggestion}</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }

                // No issues found
                if (!data.memory_leaks?.length && !data.code_analysis?.length) {
                    resultsHtml += `
                        <div class="analysis-card">
                            <div class="analysis-card-header text-green-400">
                                Analysis Complete
                            </div>
                            <div class="analysis-card-content">
                                <div class="text-center">
                                    <svg class="w-12 h-12 mx-auto mb-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                    </svg>
                                    <div class="text-gray-300">No issues found in your code!</div>
                                </div>
                            </div>
                        </div>
                    `;
                }

                resultsHtml += '</div>';
                analysisOutput.innerHTML = resultsHtml;

            } catch (error) {
                console.error('Analysis error:', error);
                analysisOutput.innerHTML = `
                    <div class="analysis-card">
                        <div class="analysis-card-header text-red-400">Error</div>
                        <div class="analysis-card-content">Failed to analyze code. Please try again.</div>
                    </div>
                `;
            }
        });
    }

    // Format Code
    if (formatCode) {
        formatCode.addEventListener('click', async () => {
            try {
                const code = window.editor.getValue();
                const language = languageSelect.value;
                
                formatCode.disabled = true;
                formatCode.innerHTML = `
                    <svg class="animate-spin w-4 h-4 mr-1" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Formatting...
                `;
                
                const response = await fetch('/format', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, language })
                });
                
                if (!response.ok) {
                    throw new Error(`Format failed: ${response.statusText}`);
                }
                
                const data = await response.json();
                if (data.formatted) {
                    window.editor.setValue(data.formatted);
                }
            } catch (error) {
                console.error('Format error:', error);
                analysisOutput.innerHTML = `
                    <div class="analysis-card">
                        <div class="analysis-card-header text-red-400">Format Error</div>
                        <div class="analysis-card-content">${error.message}</div>
                    </div>
                `;
            } finally {
                formatCode.disabled = false;
                formatCode.innerHTML = `
                    <svg class="w-4 h-4 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"/>
                    </svg>
                    Format
                `;
            }
        });
    }

    // Share Code
    if (shareCode) {
        shareCode.addEventListener('click', async () => {
            try {
                const code = window.editor.getValue();
                const language = languageSelect.value;
                const response = await fetch('/share', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, language })
                });
                const data = await response.json();
                if (data.url) {
                    navigator.clipboard.writeText(data.url);
                    alert('Share URL copied to clipboard!');
                }
            } catch (error) {
                console.error('Share error:', error);
            }
        });
    }
});

function createAnalysisCard(title, items) {
    return `
        <div class="analysis-card">
            <div class="analysis-card-header">
                ${title}
            </div>
            <div class="analysis-card-content">
                ${items.map(item => `
                    <div class="mb-4 last:mb-0">
                        <div class="flex justify-between items-start">
                            <div class="font-medium text-[#dfe1e5]">${item.title}</div>
                            <div class="text-sm text-[#9da0a5]">Line ${item.line}</div>
                        </div>
                        <div class="mt-1 text-sm text-[#9da0a5]">${item.description}</div>
                        ${item.severity ? `
                            <div class="mt-1 text-sm">
                                <span class="text-${getSeverityColor(item.severity)}-400">
                                    ${item.severity.charAt(0).toUpperCase() + item.severity.slice(1)} Severity
                                </span>
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function getSeverityColor(severity) {
    switch (severity.toLowerCase()) {
        case 'high': return 'red';
        case 'medium': return 'yellow';
        case 'low': return 'green';
        default: return 'blue';
    }
} 