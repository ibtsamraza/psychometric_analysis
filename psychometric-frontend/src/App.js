import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import PizZip from 'pizzip';
import Docxtemplater from 'docxtemplater';
import { saveAs } from 'file-saver';
import ReactMarkdown from 'react-markdown';
import { marked } from 'marked';

function App() {
  const [files, setFiles] = useState({ scores: null, items: null });
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loadingMessage, setLoadingMessage] = useState("Processing your files...");
  const [processingStep, setProcessingStep] = useState(0);
  const [processingSteps] = useState([
    "Uploading files",
    "Extracting data",
    "Analyzing scores",
    "Processing items",
    "Generating insights"
  ]);
  const [socketStatus, setSocketStatus] = useState('Not connected');
  const [processingStatus, setProcessingStatus] = useState('');
  const [processingProgress, setProcessingProgress] = useState(0);
  const [agentStatus, setAgentStatus] = useState({
    agent: '',
    status: '',
    progress: 0,
    name: ''
  });
  const [sessionId, setSessionId] = useState(null);

  const handleFileChange = (e) => {
    const { name, files: selectedFiles } = e.target;
    setFiles(prev => ({
      ...prev,
      [name]: selectedFiles[0]
    }));
  };

  useEffect(() => {
    if (!sessionId) {
      setSocketStatus('Waiting for session ID');
      return;
    }
    
    console.log("Setting up SSE connection for session:", sessionId);
    setSocketStatus('Connecting via SSE...');
    
    const sseUrl = `/events/${sessionId}`;
    console.log("SSE URL:", sseUrl);
    
    let eventSource = null;
    try {
      eventSource = new EventSource(sseUrl);
      
      eventSource.onopen = () => {
        console.log('SSE connection opened');
        setSocketStatus('Connected via SSE');
      };
      
      eventSource.addEventListener('update', (event) => {
        try {
          console.log("Raw SSE data received:", event.data);
          
          // Try to parse as JSON first
          let data;
          try {
            data = JSON.parse(event.data);
          } catch (jsonError) {
            // If JSON parsing fails, try to handle Python dict format
            console.warn("JSON parsing failed, trying to handle Python dict format");
            
            // Replace single quotes with double quotes for JSON compatibility
            const jsonString = event.data
              .replace(/'/g, '"')
              .replace(/None/g, 'null')
              .replace(/True/g, 'true')
              .replace(/False/g, 'false');
            
            try {
              data = JSON.parse(jsonString);
            } catch (fallbackError) {
              console.error("Fallback parsing failed:", fallbackError);
              throw new Error("Could not parse event data in any format");
            }
          }
          
          console.log("Parsed SSE update:", data);
          
          // Update the UI with the received data
          setAgentStatus({
            agent: data.agent || '',
            status: data.status || '',
            progress: data.progress || 0,
            name: data.name || ''
          });
          
          // Also update the processing status and progress
          setProcessingStatus(data.status || '');
          setProcessingProgress(data.progress || 0);
        } catch (error) {
          console.error("Error processing SSE data:", error, event.data);
        }
      });
      
      eventSource.onerror = (error) => {
        console.error("SSE error:", error);
        setSocketStatus('SSE connection error');
      };
    } catch (error) {
      console.error("Error creating EventSource:", error);
      setSocketStatus(`Error creating EventSource: ${error.message}`);
    }
    
    return () => {
      if (eventSource) {
        console.log("Closing SSE connection");
        eventSource.close();
      }
    };
  }, [sessionId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setAnalysis(null);
    setProcessingProgress(0);
    setProcessingStatus('Starting analysis...');
    
    const newSessionId = Date.now().toString();
    setSessionId(newSessionId);
    
    const formData = new FormData();
    formData.append('scores_file', files.scores);
    formData.append('items_file', files.items);
    formData.append('session_id', newSessionId);

    console.log("Form data contents:");
    for (let pair of formData.entries()) {
      console.log(pair[0] + ': ' + pair[1]);
    }

    try {
      const response = await fetch('/analyze/', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      console.log("Response data:", data);
      
      if (!response.ok) {
        if (data && data.error) {
          throw new Error(data.error);
        } else if (data && data.detail) {
          const errorMessage = Array.isArray(data.detail) 
            ? data.detail.map(err => err.msg).join(', ')
            : data.detail;
          throw new Error(errorMessage);
        } else {
          throw new Error('Analysis failed with status: ' + response.status);
        }
      }
      
      if (data && data.error) {
        throw new Error(data.error);
      }

      setAnalysis(data);
      
      setProcessingStep(processingSteps.length - 1);
    } catch (err) {
      console.error('Error during fetch:', err);
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const generateWordDocument = async () => {
    const response    = await fetch('/template.docx');
    const arrayBuffer = await response.arrayBuffer();
    const zip         = new PizZip(arrayBuffer);
  
    const doc = new Docxtemplater(zip, {
      paragraphLoop: true,
      linebreaks:    true,
    });
  
    const allAnalyses = analysis.analyses.map(item => ({
      sheet_name:            item.sheet_name,
      psychometric_analysis: item.analysis["Psychometric Analysis"],
      item_analysis:         item.analysis["Item Analysis"],
    }));
  
    console.log('DOCX DATA CONTEXT:', allAnalyses);
  
    doc.setData({ analyses: allAnalyses });
    try {
      doc.render();
      const out = doc.getZip().generate({
        type:     "blob",
        mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      saveAs(out, 'all_analyses.docx');
    } catch (err) {
      console.error('Error rendering template:', err);
      setError('Error generating Word document: ' + err.message);
    }
  };
  
  const testSocketConnection = () => {
    console.log("Testing server connection...");
    fetch(`/ping`)
      .then(response => response.json())
      .then(data => {
        console.log("Server ping response:", data);
        setSocketStatus(`Server ping successful: ${new Date(data.timestamp * 1000).toLocaleTimeString()}`);
      })
      .catch(error => {
        console.error("Error pinging server:", error);
        setSocketStatus(`Server ping failed: ${error.message}`);
      });
  };

  const testProgressUpdates = () => {
    if (!sessionId) {
      const testId = 'test-' + Date.now().toString();
      setSessionId(testId);
      console.log("Created test session ID for progress test:", testId);
      return;
    }
    
    console.log("Testing progress updates...");
    fetch(`/test-progress/${sessionId}`)
      .then(response => response.json())
      .then(data => {
        console.log("Test progress response:", data);
      })
      .catch(error => {
        console.error("Error testing progress:", error);
      });
  };

  const setTestSessionId = () => {
    const testId = 'test-' + Date.now().toString();
    setSessionId(testId);
    console.log("Set test session ID:", testId);
  };

  const testSSE = () => {
    if (!sessionId) {
      const testId = 'test-' + Date.now().toString();
      setSessionId(testId);
      console.log("Created test session ID for SSE:", testId);
    }
    
    console.log("Testing SSE updates...");
    fetch(`/test-progress/${sessionId}`)
      .then(response => response.json())
      .then(data => {
        console.log("Test progress response:", data);
      })
      .catch(error => {
        console.error("Error testing progress:", error);
      });
  };

  const testBackendAccess = () => {
    console.log("Testing backend access...");
    
    // Test basic endpoint
    fetch('/ping')
      .then(response => {
        if (!response.ok) throw new Error(`Status: ${response.status}`);
        return response.json();
      })
      .then(data => {
        console.log("Ping response:", data);
        setSocketStatus(`Backend accessible: ${JSON.stringify(data)}`);
        
        // Now test SSE endpoint
        return fetch(`/status/${sessionId || 'test-' + Date.now()}`);
      })
      .then(response => {
        if (!response.ok) throw new Error(`Status endpoint: ${response.status}`);
        return response.json();
      })
      .then(data => {
        console.log("Status response:", data);
        setSocketStatus(`Backend and status endpoint accessible`);
      })
      .catch(error => {
        console.error("Backend access error:", error);
        setSocketStatus(`Backend access error: ${error.message}`);
      });
  };

  const simulateAnalysis = () => {
    if (!sessionId) {
      const testId = 'sim-' + Date.now().toString();
      setSessionId(testId);
      console.log("Created simulation session ID:", testId);
      
      // Wait a moment for the SSE connection to establish
      setTimeout(() => {
        console.log("Starting simulation for session:", testId);
        fetch(`/simulate-analysis/${testId}`)
          .then(response => response.json())
          .then(data => {
            console.log("Simulation response:", data);
          })
          .catch(error => {
            console.error("Error starting simulation:", error);
          });
      }, 1000);
    } else {
      console.log("Starting simulation for existing session:", sessionId);
      fetch(`/simulate-analysis/${sessionId}`)
        .then(response => response.json())
        .then(data => {
          console.log("Simulation response:", data);
        })
        .catch(error => {
          console.error("Error starting simulation:", error);
        });
    }
  };

  if (window.location.protocol !== 'https:' && !window.location.hostname.includes('localhost')) {
    window.location.href = 'https:' + window.location.href.substring(window.location.protocol.length);
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>📊 Psychometric Analyzer</h1>
        <p className="subheading">Upload Excel files and generate insights + Word report</p>
      </header>

      <main className="App-main">

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-group">
            <label htmlFor="scores">Scores File:</label>
            <input
              type="file"
              id="scores"
              name="scores"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
              required
            />
          </div>

          <div className="file-input-group">
            <label htmlFor="items">Items File:</label>
            <input
              type="file"
              id="items"
              name="items"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
              required
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : '🔍 Analyze Now'}
          </button>
        </form>
        {error && (
            <div className="error-container">
              <div className="error-message">
                <p><strong>Error:</strong> {error}</p>
              </div>
            </div>
          )}



        {analysis?.analyses?.length > 0 && (
          <section className="analysis-results">
            <h2>✅ Analysis Results</h2>
            {analysis.analyses.map((sheetAnalysis, index) => (
              <div key={index} className="sheet-analysis">
                <h3>📄 Sheet: {sheetAnalysis.sheet_name}</h3>
                <div className="analysis-content">
                  <h4>🧠 Psychometric Analysis</h4>
                  <ReactMarkdown>{sheetAnalysis.analysis["Psychometric Analysis"]}</ReactMarkdown>
                  
                  <h4>🧪 Item Analysis</h4>
                  <ReactMarkdown>{sheetAnalysis.analysis["Item Analysis"]}</ReactMarkdown>
                  
                </div>
              </div>
            ))}
            <button className="download-btn" onClick={generateWordDocument}>
              ⬇️ Download Word Document
            </button>
          </section>
        )}



        {loading && (
          <div className="agent-progress-container">
            <h3>
              {agentStatus.name ? `${agentStatus.name} Analysis in Progress` : 'Initiating Psychometric Analysis'}
            </h3>
            
            <div className="progress-bar-container">
              <div 
                className="progress-bar" 
                style={{ width: `${agentStatus.progress}%` }}
              ></div>
            </div>
            
            <div className="agent-status">
              <p className="agent-name">
                {agentStatus.agent === 'psychometric_analysis' && '🧠 Psychometric Analysis'}
                {agentStatus.agent === 'check_missing' && '🔍 Checking Analysis Completeness'}
                {agentStatus.agent === 'judge_analysis' && '⚖️ Evaluating Analysis Quality'}
                {agentStatus.agent === 'correlated_analysis' && '🔄 Analyzing Correlated Domains'}
                {agentStatus.agent === 'check_bias' && '⚠️ Checking Response Bias'}
                {agentStatus.agent === 'item_analysis' && '📊 Item-Level Analysis'}
                {agentStatus.agent === 'complete' && '✅ Analysis Complete'}
                {agentStatus.agent === 'error' && '❌ Error'}
                {!agentStatus.agent && 'Starting...'}
              </p>
              <p className="agent-status-message">{agentStatus.status}</p>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
