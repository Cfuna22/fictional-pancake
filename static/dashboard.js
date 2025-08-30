/**
 * Dashboard JavaScript for CRM Sentiment Data Generator
 * Handles charts, AI recommendations, and interactive features
 */

// Chart.js configuration for dark theme
Chart.defaults.color = '#ffffff';
Chart.defaults.backgroundColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.2)';

// Global chart instances
let sentimentByRegionChart = null;
let churnRiskChart = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    loadRecommendations();
    setupInteractiveFeatures();
});

/**
 * Initialize all charts on the dashboard
 */
function initializeCharts() {
    // Load sample data for charts
    fetch('/api/sample-data')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading chart data:', data.error);
                showChartError();
                return;
            }
            
            createSentimentByRegionChart(data.sentiment_by_region);
            createChurnRiskChart(data.churn_risk_distribution);
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
            showChartError();
        });
}

/**
 * Create sentiment by region bar chart
 */
function createSentimentByRegionChart(data) {
    const ctx = document.getElementById('sentimentByRegionChart');
    if (!ctx) return;

    const regions = Object.keys(data);
    const sentimentValues = Object.values(data);

    // Create color array based on sentiment values
    const colors = sentimentValues.map(value => {
        if (value > 0.2) return 'rgba(25, 135, 84, 0.8)'; // Green for positive
        if (value < -0.2) return 'rgba(220, 53, 69, 0.8)'; // Red for negative
        return 'rgba(255, 193, 7, 0.8)'; // Yellow for neutral
    });

    sentimentByRegionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: regions,
            datasets: [{
                label: 'Average Sentiment Score',
                data: sentimentValues,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.8', '1')),
                borderWidth: 2,
                borderRadius: 4,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.y;
                            const sentiment = value > 0.2 ? 'Positive' : value < -0.2 ? 'Negative' : 'Neutral';
                            return `Sentiment: ${value.toFixed(3)} (${sentiment})`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    min: -1,
                    max: 1,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff',
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

/**
 * Create churn risk distribution pie chart
 */
function createChurnRiskChart(data) {
    const ctx = document.getElementById('churnRiskChart');
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);

    churnRiskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(25, 135, 84, 0.8)',   // Low - Green
                    'rgba(255, 193, 7, 0.8)',   // Medium - Yellow
                    'rgba(220, 53, 69, 0.8)'    // High - Red
                ],
                borderColor: [
                    'rgba(25, 135, 84, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff',
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const label = context.label;
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} customers (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '50%',
            animation: {
                animateRotate: true,
                animateScale: false
            }
        }
    });
}

/**
 * Load AI recommendations from the server
 */
function loadRecommendations() {
    const recommendationsContainer = document.getElementById('recommendations-content');
    if (!recommendationsContainer) return;

    fetch('/api/recommendations')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showRecommendationsError(data.error);
                return;
            }
            
            displayRecommendations(data);
        })
        .catch(error => {
            console.error('Error loading recommendations:', error);
            showRecommendationsError('Failed to load recommendations. Please try again.');
        });
}

/**
 * Display AI recommendations in the dashboard
 */
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-content');
    if (!container) return;

    let html = '';

    // Priority Actions
    if (recommendations.priority_actions && recommendations.priority_actions.length > 0) {
        html += `
            <div class="mb-4">
                <h6 class="text-danger mb-3">
                    <i class="fas fa-exclamation-triangle me-2"></i>Priority Actions
                </h6>
                <div class="row">
        `;
        
        recommendations.priority_actions.forEach(action => {
            const priorityColor = action.priority === 'High' ? 'danger' : action.priority === 'Medium' ? 'warning' : 'info';
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card bg-${priorityColor} bg-opacity-10 border-${priorityColor}">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <span class="badge bg-${priorityColor}">${action.priority} Priority</span>
                                <small class="text-muted">${action.metric}</small>
                            </div>
                            <p class="card-text small mb-1">${action.action}</p>
                            <small class="text-muted">${action.impact}</small>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div></div>';
    }

    // Revenue Opportunities
    if (recommendations.revenue_opportunities && recommendations.revenue_opportunities.length > 0) {
        html += `
            <div class="mb-4">
                <h6 class="text-success mb-3">
                    <i class="fas fa-dollar-sign me-2"></i>Revenue Opportunities
                </h6>
                <div class="list-group list-group-flush">
        `;
        
        recommendations.revenue_opportunities.forEach(opportunity => {
            html += `
                <div class="list-group-item bg-transparent border-success border-opacity-25">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1 text-success">${opportunity.opportunity}</h6>
                            <p class="mb-1 small">${opportunity.action}</p>
                        </div>
                        <small class="text-success">${opportunity.potential}</small>
                    </div>
                </div>
            `;
        });
        
        html += '</div></div>';
    }

    // Key Insights
    if (recommendations.operational_insights && recommendations.operational_insights.length > 0) {
        html += `
            <div class="mb-4">
                <h6 class="text-info mb-3">
                    <i class="fas fa-lightbulb me-2"></i>Key Insights
                </h6>
                <div class="row">
        `;
        
        recommendations.operational_insights.slice(0, 3).forEach(insight => {
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card bg-info bg-opacity-10 border-info">
                        <div class="card-body">
                            <h6 class="card-title text-info small">${insight.insight}</h6>
                            <p class="card-text small mb-2">${insight.detail}</p>
                            <small class="text-muted">${insight.recommendation}</small>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div></div>';
    }

    // Success Metrics Summary
    if (recommendations.success_metrics) {
        const metrics = recommendations.success_metrics;
        html += `
            <div class="mb-3">
                <h6 class="text-secondary mb-3">
                    <i class="fas fa-chart-bar me-2"></i>Performance Summary
                </h6>
                <div class="row text-center">
                    <div class="col-3">
                        <div class="border rounded p-2">
                            <div class="text-warning h6 mb-1">${metrics.customer_satisfaction?.positive_sentiment_rate || 0}%</div>
                            <small class="text-muted">Positive Sentiment</small>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="border rounded p-2">
                            <div class="text-success h6 mb-1">${metrics.churn_metrics?.low_risk_rate || 0}%</div>
                            <small class="text-muted">Low Churn Risk</small>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="border rounded p-2">
                            <div class="text-info h6 mb-1">${metrics.operational_metrics?.resolution_rate || 0}%</div>
                            <small class="text-muted">Resolution Rate</small>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="border rounded p-2">
                            <div class="text-primary h6 mb-1">${metrics.sales_metrics?.win_rate || 0}%</div>
                            <small class="text-muted">Win Rate</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

/**
 * Show error message when chart data fails to load
 */
function showChartError() {
    const chartContainers = ['sentimentByRegionChart', 'churnRiskChart'];
    
    chartContainers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>Unable to load chart data</p>
                </div>
            `;
        }
    });
}

/**
 * Show error message when recommendations fail to load
 */
function showRecommendationsError(message) {
    const container = document.getElementById('recommendations-content');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-warning" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
            <div class="text-center">
                <button class="btn btn-outline-primary btn-sm" onclick="loadRecommendations()">
                    <i class="fas fa-sync-alt me-1"></i> Retry
                </button>
            </div>
        `;
    }
}

/**
 * Setup interactive features for the dashboard
 */
function setupInteractiveFeatures() {
    // Add hover effects to metric cards
    const metricCards = document.querySelectorAll('.card[class*="bg-primary"], .card[class*="bg-success"], .card[class*="bg-warning"], .card[class*="bg-danger"]');
    metricCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.2s ease-in-out';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add click handlers for table sorting (if needed)
    const tableHeaders = document.querySelectorAll('th[data-sortable="true"]');
    tableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            // Basic table sorting logic could be added here
            console.log('Sorting by:', this.textContent);
        });
    });

    // Refresh data button functionality
    const refreshButton = document.querySelector('[data-action="refresh"]');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-sync-alt fa-spin me-1"></i> Refreshing...';
            
            // Reload charts and recommendations
            initializeCharts();
            loadRecommendations();
            
            setTimeout(() => {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-sync-alt me-1"></i> Refresh Data';
            }, 2000);
        });
    }

    // Add tooltips to badges and metrics
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Utility function to format numbers for display
 */
function formatNumber(num, type = 'default') {
    if (typeof num !== 'number') return num;
    
    switch (type) {
        case 'currency':
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(num);
        case 'percentage':
            return new Intl.NumberFormat('en-US', {
                style: 'percent',
                minimumFractionDigits: 1,
                maximumFractionDigits: 1
            }).format(num / 100);
        case 'decimal':
            return new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(num);
        default:
            return new Intl.NumberFormat('en-US').format(num);
    }
}

/**
 * Export functionality for charts (optional)
 */
function exportChart(chartId, filename) {
    const chart = chartId === 'sentiment' ? sentimentByRegionChart : churnRiskChart;
    if (chart) {
        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${filename}.png`;
        link.href = url;
        link.click();
    }
}

// Cleanup function for when the page is unloaded
window.addEventListener('beforeunload', function() {
    if (sentimentByRegionChart) {
        sentimentByRegionChart.destroy();
    }
    if (churnRiskChart) {
        churnRiskChart.destroy();
    }
});

// Error handling for uncaught errors
window.addEventListener('error', function(event) {
    console.error('Dashboard error:', event.error);
});

// Handle fetch errors globally
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});
