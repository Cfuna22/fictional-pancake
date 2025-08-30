import os
import logging
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from data_generator import CRMDataGenerator
from recommendations import AIRecommendations
import io
import zipfile

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "hackathon-crm-dashboard-2024")

# Initialize data generator and AI recommendations
data_generator = CRMDataGenerator()
ai_recommendations = AIRecommendations()

@app.route('/')
def index():
    """Main landing page with options to generate data and view guides"""
    return render_template('index.html')

@app.route('/generate-data', methods=['POST'])
def generate_data():
    """Generate CRM and sentiment data based on user parameters"""
    try:
        # Get parameters from form
        num_customers = int(request.form.get('num_customers', 500))
        regions = request.form.getlist('regions')
        segments = request.form.getlist('segments')
        
        if not regions:
            regions = ['North America', 'Europe', 'APAC']
        if not segments:
            segments = ['SMB', 'Mid-Market', 'Enterprise']
        
        # Generate the datasets
        customers_df, deals_df, feedback_df, summary_stats = data_generator.generate_complete_dataset(
            num_customers=num_customers,
            regions=regions,
            segments=segments
        )
        
        # Store in session or cache for download
        app.config['generated_data'] = {
            'customers': customers_df,
            'deals': deals_df,
            'feedback': feedback_df,
            'stats': summary_stats
        }
        
        flash(f'Successfully generated data for {num_customers} customers!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logging.error(f"Error generating data: {str(e)}")
        flash(f'Error generating data: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Display generated data preview and download options"""
    if 'generated_data' not in app.config:
        flash('No data generated yet. Please generate data first.', 'warning')
        return redirect(url_for('index'))
    
    data = app.config['generated_data']
    return render_template('dashboard.html', 
                         customers=data['customers'].head(10),
                         deals=data['deals'].head(10),
                         feedback=data['feedback'].head(10),
                         stats=data['stats'])

@app.route('/download-csv/<dataset>')
def download_csv(dataset):
    """Download individual CSV files"""
    if 'generated_data' not in app.config:
        flash('No data available for download', 'error')
        return redirect(url_for('index'))
    
    data = app.config['generated_data']
    
    if dataset == 'customers':
        df = data['customers']
        filename = 'crm_customers.csv'
    elif dataset == 'deals':
        df = data['deals']
        filename = 'crm_deals.csv'
    elif dataset == 'feedback':
        df = data['feedback']
        filename = 'customer_feedback.csv'
    else:
        flash('Invalid dataset requested', 'error')
        return redirect(url_for('dashboard'))
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Convert to bytes
    csv_bytes = io.BytesIO()
    csv_bytes.write(output.getvalue().encode('utf-8'))
    csv_bytes.seek(0)
    
    return send_file(csv_bytes, 
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=filename)

@app.route('/download-all')
def download_all():
    """Download all CSV files as a ZIP"""
    if 'generated_data' not in app.config:
        flash('No data available for download', 'error')
        return redirect(url_for('index'))
    
    data = app.config['generated_data']
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add customers CSV
        customers_csv = io.StringIO()
        data['customers'].to_csv(customers_csv, index=False)
        zip_file.writestr('crm_customers.csv', customers_csv.getvalue())
        
        # Add deals CSV
        deals_csv = io.StringIO()
        data['deals'].to_csv(deals_csv, index=False)
        zip_file.writestr('crm_deals.csv', deals_csv.getvalue())
        
        # Add feedback CSV
        feedback_csv = io.StringIO()
        data['feedback'].to_csv(feedback_csv, index=False)
        zip_file.writestr('customer_feedback.csv', feedback_csv.getvalue())
        
        # Add Tableau guide
        tableau_guide = """# Tableau Integration Guide

## Step 1: Import Data
1. Open Tableau Desktop
2. Connect to Text File
3. Import all three CSV files:
   - crm_customers.csv
   - crm_deals.csv
   - customer_feedback.csv

## Step 2: Create Relationships
1. Drag tables to relationship canvas
2. Connect Customer_ID fields between tables
3. Verify data relationships

## Step 3: Build Dashboard
See the web application for detailed instructions.
"""
        zip_file.writestr('tableau_integration_guide.txt', tableau_guide)
    
    zip_buffer.seek(0)
    
    return send_file(zip_buffer,
                     mimetype='application/zip',
                     as_attachment=True,
                     download_name='crm_sentiment_data.zip')

@app.route('/api/recommendations')
def get_recommendations():
    """Get AI-powered recommendations based on generated data"""
    if 'generated_data' not in app.config:
        return jsonify({'error': 'No data available'}), 400
    
    data = app.config['generated_data']
    recommendations = ai_recommendations.generate_recommendations(
        data['customers'], 
        data['deals'], 
        data['feedback']
    )
    
    return jsonify(recommendations)

@app.route('/tableau-guide')
def tableau_guide():
    """Display comprehensive Tableau integration guide"""
    return render_template('tableau_guide.html')

@app.route('/api/sample-data')
def get_sample_data():
    """Get sample data for preview charts"""
    if 'generated_data' not in app.config:
        return jsonify({'error': 'No data available'}), 400
    
    data = app.config['generated_data']
    
    # Prepare data for charts
    sentiment_by_region = data['feedback'].groupby('Region')['Sentiment_Score'].mean().to_dict()
    churn_risk_distribution = data['feedback']['Churn_Risk'].value_counts().to_dict()
    
    # Sentiment trend over time (mock monthly data)
    import pandas as pd
    feedback_with_dates = data['feedback'].copy()
    feedback_with_dates['Month'] = pd.date_range(start='2024-01-01', periods=len(feedback_with_dates), freq='D').strftime('%Y-%m')
    sentiment_trend = feedback_with_dates.groupby('Month')['Sentiment_Score'].mean().to_dict()
    
    return jsonify({
        'sentiment_by_region': sentiment_by_region,
        'churn_risk_distribution': churn_risk_distribution,
        'sentiment_trend': sentiment_trend
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
