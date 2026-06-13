"use client";

import React, { useState, useEffect } from "react";
import { useApp } from "../../context/AppContext";
import { 
  Settings, 
  Key, 
  Database, 
  FileText, 
  Save, 
  CheckCircle,
  Eye,
  EyeOff,
  Cloud
} from "lucide-react";
import styles from "./page.module.css";
import { API_BASE_URL } from "../../config";

const SettingsPage: React.FC = () => {
  const { activeProfile, refreshAll } = useApp();

  // API credentials states
  const [nvidiaKey, setNvidiaKey] = useState("••••••••••••••••••••••••");
  const [geminiKey, setGeminiKey] = useState("••••••••••••••••••••••••");
  const [showNvidia, setShowNvidia] = useState(false);
  const [showGemini, setShowGemini] = useState(false);

  // Firebase configurations
  const [firebaseApiKey, setFirebaseApiKey] = useState("");
  const [firebaseProjectId, setFirebaseProjectId] = useState("");

  const [savingKeys, setSavingKeys] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Fetch current configs from backend dev endpoints if available
  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then(res => res.json())
      .then(data => {
        // Backend keys exist
      })
      .catch(e => console.error(e));
  }, []);

  const handleSaveKeys = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingKeys(true);
    
    // Simulate updating keys or store locally in memory for session
    setTimeout(() => {
      setSavingKeys(false);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    }, 1200);
  };

  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <div>
          <h1>System Settings</h1>
          <p>Configure model keys, Firebase Auth integrations, and manage your parsed candidate profile.</p>
        </div>
      </div>

      <div className={styles.splitSection}>
        {/* Left Side: Keys Configuration */}
        <section className={styles.configPanel}>
          <div className={styles.panelTitleGroup}>
            <Key size={18} />
            <h3>LLM &amp; Cloud Keys</h3>
          </div>
          
          <form onSubmit={handleSaveKeys} className={styles.form}>
            <div className={styles.formGroup}>
              <label>Nvidia NIM API Key</label>
              <div className={styles.inputWrapper}>
                <input 
                  type={showNvidia ? "text" : "password"} 
                  className="form-input" 
                  value={nvidiaKey}
                  onChange={(e) => setNvidiaKey(e.target.value)}
                  placeholder="nvapi-..."
                />
                <button 
                  type="button" 
                  className={styles.eyeBtn}
                  onClick={() => setShowNvidia(!showNvidia)}
                >
                  {showNvidia ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <span className={styles.helpText}>Used to generate matching components and custom outreach email drafts.</span>
            </div>

            <div className={styles.formGroup}>
              <label>Google Gemini API Key</label>
              <div className={styles.inputWrapper}>
                <input 
                  type={showGemini ? "text" : "password"} 
                  className="form-input" 
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  placeholder="AIzaSy..."
                />
                <button 
                  type="button" 
                  className={styles.eyeBtn}
                  onClick={() => setShowGemini(!showGemini)}
                >
                  {showGemini ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <span className={styles.helpText}>Used for background fallback scrapers and deep company research.</span>
            </div>

            <div className={styles.formGroup}>
              <label>Firebase API Key</label>
              <input 
                type="text" 
                className="form-input" 
                value={firebaseApiKey}
                onChange={(e) => setFirebaseApiKey(e.target.value)}
                placeholder="AIzaSyBw..."
              />
            </div>

            <div className={styles.formGroup}>
              <label>Firebase Project ID</label>
              <input 
                type="text" 
                className="form-input" 
                value={firebaseProjectId}
                onChange={(e) => setFirebaseProjectId(e.target.value)}
                placeholder="career-copilot-auth"
              />
            </div>

            <button 
              type="submit" 
              className="btn-primary" 
              disabled={savingKeys}
              style={{ width: "100%", marginTop: "1rem" }}
            >
              <Save size={16} />
              <span>{savingKeys ? "Saving Config..." : savedSuccess ? "Config Saved!" : "Save Settings"}</span>
            </button>
          </form>
        </section>

        {/* Right Side: Resume Parsing Meta & Details */}
        <section className={styles.profilePanel}>
          <div className={styles.panelTitleGroup}>
            <FileText size={18} />
            <h3>Parsed Profile Summary</h3>
          </div>

          {activeProfile ? (
            <div className={styles.profileDetails}>
              <div className={styles.profileMetaRow}>
                <span className={styles.metaLabel}>Profile Status:</span>
                <span className={styles.activeBadge}>Active &amp; Ready</span>
              </div>
              
              <div className={styles.profileMetaRow}>
                <span className={styles.metaLabel}>Resume Version:</span>
                <span>V{activeProfile.version}</span>
              </div>

              <div className={styles.profileMetaRow}>
                <span className={styles.metaLabel}>Parsed On:</span>
                <span>{new Date(activeProfile.uploaded_at).toLocaleString()}</span>
              </div>

              <div className={styles.skillsBox}>
                <h4>Parsed Skills ({Object.keys(activeProfile.skills || {}).length})</h4>
                <div className={styles.skillsCloud}>
                  {Object.keys(activeProfile.skills || {}).map(skill => (
                    <span key={skill} className={styles.skillTag}>{skill}</span>
                  ))}
                </div>
              </div>

              <div className={styles.experienceSummary}>
                <h4>Work History Profile</h4>
                <p>
                  Found {activeProfile.experience?.length || 0} previous job roles and {activeProfile.education?.length || 0} education references.
                </p>
              </div>
            </div>
          ) : (
            <div className={styles.noProfile}>
              <Cloud size={44} className={styles.cloudIcon} />
              <h4>No Active Candidate Profile</h4>
              <p>Go to the main header and upload your resume PDF to view the parsed skill analysis and profile structure.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default SettingsPage;
