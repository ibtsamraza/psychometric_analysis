import React, { useState } from 'react';
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

  const handleFileChange = (e) => {
    const { name, files: selectedFiles } = e.target;
    setFiles(prev => ({
      ...prev,
      [name]: selectedFiles[0]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setAnalysis(null);

    const formData = new FormData();
    formData.append('scores_file', files.scores);
    formData.append('items_file', files.items);

    try {
      const response = await fetch('http://localhost:8000/analyze/', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Analysis failed');
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      console.error('Error during fetch:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateWordDocument = async () => {
    // 1) Fetch template from public/
    const response    = await fetch('/template.docx');
    const arrayBuffer = await response.arrayBuffer();
    const zip         = new PizZip(arrayBuffer);
  
    // 2) Init Docxtemplater
    const doc = new Docxtemplater(zip, {
      paragraphLoop: true,
      linebreaks:    true,
    });
  
    // 3) Build data context
    const allAnalyses = analysis.analyses.map(item => ({
      sheet_name:            item.sheet_name,
      psychometric_analysis: item.analysis["Psychometric Analysis"],
      item_analysis:         item.analysis["Item Analysis"],
    }));
  
    // 4) Debug log
    console.log('DOCX DATA CONTEXT:', allAnalyses);
  
    // 5) Set data and render
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
    }
  };
  

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

        {error && <div className="error-message">⚠️ {error}</div>}

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
      </main>
    </div>
  );
}

export default App;
