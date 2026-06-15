"use client";

import React, { useState } from "react";
import { useApp, Application, Job } from "../../context/AppContext";
import { 
  Trophy, 
  MapPin, 
  Trash2, 
  Plus, 
  MessageSquare, 
  Calendar, 
  CheckSquare,
  ArrowRight,
  TrendingUp
} from "lucide-react";
import styles from "./page.module.css";

interface Column {
  id: string;
  title: string;
  color: string;
}

const KANBAN_COLUMNS: Column[] = [
  { id: "interested", title: "Interested", color: "#60a5fa" },
  { id: "applied", title: "Applied", color: "#818cf8" },
  { id: "interviewing", title: "Interviewing", color: "#fbbf24" },
  { id: "offer", title: "Offer", color: "#34d399" },
  { id: "rejected", title: "Archive", color: "#f87171" }
];

const KanbanPage: React.FC = () => {
  const { 
    applications, 
    jobs, 
    updateApplication, 
    deleteApplication 
  } = useApp();

  const [activeModalApp, setActiveModalApp] = useState<Application | null>(null);
  const [modalNotes, setModalNotes] = useState("");

  const getJobForApplication = (app: Application): Job | undefined => {
    return jobs.find(j => j.id === app.job_id);
  };

  const handleMoveStage = async (app: Application, nextStatus: string) => {
    try {
      await updateApplication(app.id, { status: nextStatus });
    } catch (e) {
      console.error(e);
      alert("Failed to update status.");
    }
  };

  const handleDelete = async (appId: string) => {
    if (confirm("Are you sure you want to stop tracking this job application?")) {
      try {
        await deleteApplication(appId);
        if (activeModalApp?.id === appId) setActiveModalApp(null);
      } catch (e) {
        console.error(e);
        alert("Failed to delete.");
      }
    }
  };

  const openEditModal = (app: Application) => {
    setActiveModalApp(app);
    setModalNotes(app.notes || "");
  };

  const handleSaveNotes = async () => {
    if (!activeModalApp) return;
    try {
      await updateApplication(activeModalApp.id, { notes: modalNotes });
      setActiveModalApp(null);
    } catch (e) {
      console.error(e);
      alert("Failed to save notes.");
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <div>
          <h1>Application Pipeline</h1>
          <p>Track your applications across interview phases and get automated reminders.</p>
        </div>
      </div>

      {/* Kanban Board Layout */}
      <div className={styles.board}>
        {KANBAN_COLUMNS.map((column) => {
          const colApps = applications.filter(app => app.status === column.id);

          return (
            <div key={column.id} className={styles.column}>
              <div className={styles.columnHeader}>
                <div className={styles.colTitleGroup}>
                  <div className={styles.colIndicator} style={{ backgroundColor: column.color }} />
                  <h3>{column.title}</h3>
                </div>
                <span className={styles.colCount}>{colApps.length}</span>
              </div>

              <div className={styles.cardsList}>
                {colApps.length === 0 ? (
                  <div className={styles.emptyCol}>
                    <p>No jobs here</p>
                  </div>
                ) : (
                  colApps.map((app) => {
                    const job = getJobForApplication(app);
                    if (!job) return null;

                    return (
                      <div 
                        key={app.id} 
                        className={styles.card}
                        onClick={() => openEditModal(app)}
                      >
                        <div className={styles.cardHeader}>
                          <span className={styles.companyName}>{job.company}</span>
                          {job.match_score && (
                            <span 
                              className={styles.scoreBadge}
                              style={{ 
                                color: job.match_score >= 75 ? "var(--score-high)" : "var(--score-medium)",
                                borderColor: job.match_score >= 75 ? "var(--score-high)" : "var(--score-medium)" 
                              }}
                            >
                              {Math.round(job.match_score)}% Match
                            </span>
                          )}
                        </div>

                        <h4 className={styles.jobTitle}>{job.title}</h4>

                        <div className={styles.cardMeta}>
                          <MapPin size={12} />
                          <span>{job.location}</span>
                        </div>

                        {app.notes && (
                          <div className={styles.notesSnippet}>
                            <MessageSquare size={12} />
                            <p>{app.notes}</p>
                          </div>
                        )}

                        {/* Quick transitions footer */}
                        <div 
                          className={styles.cardFooter} 
                          onClick={e => e.stopPropagation()}
                        >
                          <button 
                            className={styles.deleteBtn}
                            onClick={() => handleDelete(app.id)}
                            title="Delete tracking"
                          >
                            <Trash2 size={14} />
                          </button>

                          <div className={styles.shiftGroup}>
                            {column.id === "interested" && (
                              <button 
                                className={styles.shiftBtn}
                                onClick={() => handleMoveStage(app, "applied")}
                                title="Move to Applied"
                              >
                                <span>Applied</span>
                                <ArrowRight size={12} />
                              </button>
                            )}
                            {column.id === "applied" && (
                              <button 
                                className={styles.shiftBtn}
                                onClick={() => handleMoveStage(app, "interviewing")}
                                title="Move to Interviewing"
                              >
                                <span>Interview</span>
                                <ArrowRight size={12} />
                              </button>
                            )}
                            {column.id === "interviewing" && (
                              <button 
                                className={styles.shiftBtn}
                                onClick={() => handleMoveStage(app, "offer")}
                                title="Move to Offer"
                              >
                                <span>Offer!</span>
                                <ArrowRight size={12} />
                              </button>
                            )}
                            {column.id !== "rejected" && column.id !== "offer" && (
                              <button 
                                className={`${styles.shiftBtn} ${styles.rejectBtn}`}
                                onClick={() => handleMoveStage(app, "rejected")}
                                title="Archive Application"
                              >
                                <span>Archive</span>
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Edit Details & Notes Modal */}
      {activeModalApp && (
        <div className={styles.modalOverlay} onClick={() => setActiveModalApp(null)}>
          <div 
            className={`${styles.modalContent} animate-slideup`}
            onClick={e => e.stopPropagation()}
          >
            <div className={styles.modalHeader}>
              <div>
                <span>Edit Tracking Details</span>
                <h2>{getJobForApplication(activeModalApp)?.title}</h2>
                <p>{getJobForApplication(activeModalApp)?.company}</p>
              </div>
              <button 
                className={styles.modalClose}
                onClick={() => setActiveModalApp(null)}
              >
                &times;
              </button>
            </div>

            <div className={styles.modalBody}>
              <div className={styles.formGroup}>
                <label>Status Stage</label>
                <select 
                  className="form-input"
                  value={activeModalApp.status}
                  onChange={(e) => handleMoveStage(activeModalApp, e.target.value)}
                >
                  <option value="interested">Interested</option>
                  <option value="applied">Applied</option>
                  <option value="interviewing">Interviewing</option>
                  <option value="offer">Offer</option>
                  <option value="rejected">Archive (Rejected)</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label>Notes &amp; Interview Logs</label>
                <textarea 
                  className="form-input"
                  rows={5}
                  placeholder="Record application details, key questions asked, interview followups, or salary expectations..."
                  value={modalNotes}
                  onChange={(e) => setModalNotes(e.target.value)}
                />
              </div>
            </div>

            <div className={styles.modalFooter}>
              <button 
                className="btn-secondary" 
                onClick={() => handleDelete(activeModalApp.id)}
              >
                <Trash2 size={16} />
                <span>Delete</span>
              </button>

              <button 
                className="btn-primary" 
                onClick={handleSaveNotes}
              >
                <span>Save Changes</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KanbanPage;
