"use client";

import React, { useRef } from "react";
import { useApp } from "../context/AppContext";
import { 
  Upload, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  User,
  Sparkles
} from "lucide-react";
import styles from "./Header.tsx.module.css";

const Header: React.FC = () => {
  const { 
    activeProfile, 
    uploadResume, 
    uploading, 
    wsStatus, 
    user,
    refreshAll
  } = useApp();
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      try {
        await uploadResume(e.target.files[0]);
      } catch (err) {
        alert(err instanceof Error ? err.message : "Error uploading resume");
      }
    }
  };

  const triggerUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <div className={styles.welcome}>
          <h1>Welcome, {user?.displayName || "Developer"}</h1>
          <p>Supercharge your job application search with AI agents.</p>
        </div>
      </div>

      <div className={styles.right}>
        {/* WebSocket Sync Status */}
        <div className={styles.statusGroup}>
          <div className={`${styles.pulse} ${styles[wsStatus]}`} />
          <span className={styles.statusText}>
            {wsStatus === "connected" ? "Live Connected" : wsStatus === "connecting" ? "Connecting..." : "Offline"}
          </span>
        </div>

        {/* Resume Control Panel */}
        <div className={styles.resumeWidget}>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept=".pdf" 
            style={{ display: "none" }} 
          />
          
          {activeProfile ? (
            <div className={styles.resumeInfo}>
              <CheckCircle2 size={16} className={styles.successIcon} />
              <div className={styles.resumeMeta}>
                <span className={styles.resumeLabel}>Resume V{activeProfile.version}</span>
                <span className={styles.resumeDate}>
                  {new Date(activeProfile.uploaded_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ) : (
            <div className={styles.resumeInfo}>
              <AlertCircle size={16} className={styles.warningIcon} />
              <div className={styles.resumeMeta}>
                <span className={styles.resumeLabel}>No Resume</span>
                <span className={styles.resumeDate}>Upload PDF to start</span>
              </div>
            </div>
          )}

          <button 
            className="btn-primary" 
            onClick={triggerUpload} 
            disabled={uploading}
            style={{ padding: "0.5rem 1rem", fontSize: "0.85rem" }}
          >
            {uploading ? (
              <RefreshCw size={14} className={styles.spin} />
            ) : (
              <Upload size={14} />
            )}
            <span>{activeProfile ? "Update" : "Upload"}</span>
          </button>
        </div>

        {/* Profile Avatar */}
        <div className={styles.avatar}>
          <User size={20} className={styles.avatarIcon} />
        </div>
      </div>
    </header>
  );
};

export default Header;
