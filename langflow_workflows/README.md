# Langflow Prescription Analysis Agent

This directory contains the implementation of an AI-powered prescription analysis agent using Langflow for the Chronic Kidney Disease (CKD) diagnostic system.

## Overview

The Langflow Prescription Analysis Agent is designed to:
1. Analyze doctor prescriptions in the context of CKD patient data
2. Provide AI-powered clinical insights and recommendations
3. Generate professional medical reports in PDF format

## Components

### 1. Prescription Report Generator (`models/prescription_report_generator.py`)
- Generates professional PDF medical reports
- Uses the fpdf library for PDF creation
- Formats patient information, prescription details, and AI analysis results

### 2. AI Recommender Enhancement (`models/ai_recommender.py`)
- Added `analyze_prescription` method for prescription analysis
- Integrates with Google Gemini API for AI-powered analysis
- Provides clinical insights, risk assessment, and recommendations

### 3. Flask API Endpoints (`app.py`)
- `/langflow/prescription-analysis` - Processes prescription data and generates analysis
- `/langflow/generate-report` - Generates PDF reports from analysis results

### 4. Langflow Workflow (`prescription_analysis.json`)
- Visual workflow definition for Langflow
- Contains all components needed for prescription analysis
- Can be imported directly into Langflow interface

## How It Works

1. **Data Input**: Patient data and prescription details are provided as input
2. **AI Analysis**: The system analyzes the prescription using the CKD AI recommender
3. **Report Generation**: A professional PDF report is generated with clinical insights
4. **Output**: The PDF report is made available for download

## Technologies Used

- **Langflow**: Visual workflow builder and execution engine
- **Python**: Backend processing and AI integration
- **Flask**: Web framework for API endpoints
- **Google Gemini API**: AI analysis of prescriptions
- **fpdf**: PDF generation library
- **MongoDB**: Data storage (existing infrastructure)

## Setup Instructions

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Langflow server:
   ```bash
   langflow run
   ```

3. Access the Langflow interface at `http://localhost:7860`

4. Import the workflow from `prescription_analysis.json` or create manually

## API Endpoints

The following endpoints are available for programmatic access:

- `POST /langflow/prescription-analysis`
  - Analyzes prescription and generates AI insights
  - Returns analysis results and PDF path

- `POST /langflow/generate-report`
  - Generates PDF report from analysis data
  - Returns PDF file path

## Testing

Run the test script to verify functionality:
```bash
python test_langflow_integration.py
```

Run the demonstration script to see usage instructions:
```bash
python demonstrate_langflow_agent.py
```

## Benefits

- **Visual Workflow Management**: Easy to modify and extend using Langflow's interface
- **Modular Design**: Reusable components that can be used in other workflows
- **Seamless Integration**: Works with existing CKD diagnostic system
- **Professional Reports**: Generates medical-grade PDF reports
- **AI-Powered Insights**: Leverages Google Gemini for clinical analysis
- **HIPAA Compliant**: Handles patient data securely