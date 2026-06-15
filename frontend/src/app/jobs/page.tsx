"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useApp, Job, Contact } from "../../context/AppContext";

import { 
  Search, 
  MapPin, 
  DollarSign, 
  Layers, 
  ExternalLink,
  Sparkles,
  Users,
  CheckCircle,
  FileText,
  Mail,
  Loader
} from "lucide-react";
import styles from "./page.module.css";

const JobsPage: React.FC = () => {
  const router = useRouter();
  const { 
    jobs, 
    activeProfile, 
    saveJob,
    getContacts,
    generateOutreach,
    applications,
    createApplication,
    messages
  } = useApp();

  const [search, setSearch] = useState("");
  const [minMatch, setMinMatch] = useState<number>(0);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  
  // Job Details drawer state
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loadingContacts, setLoadingContacts] = useState(false);
  const [generatingOutreachFor, setGeneratingOutreachFor] = useState<string | null>(null);
  const [applicationCreated, setApplicationCreated] = useState<string | null>(null);

  // Sync details when jobs change or selection changes
  useEffect(() => {
    if (selectedJob) {
      const updated = jobs.find(j => j.id === selectedJob.id);
      if (updated) setSelectedJob(updated);
    }
  }, [jobs, selectedJob]);

  // Load contacts when selectedJob changes
  useEffect(() => {
    if (selectedJob) {
      setLoadingContacts(true);
      getContacts(selectedJob.id)
        .then(data => setContacts(data))
        .catch(err => console.error(err))
        .finally(() => setLoadingContacts(false));
    } else {
      setContacts([]);
    }
  }, [selectedJob, getContacts]);

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(search.toLowerCase()) || 
                          job.company.toLowerCase().includes(search.toLowerCase());
    const matchesScore = (job.match_score || 0) >= minMatch;
    return matchesSearch && matchesScore;
  });

  const handleTrackJob = async (job: Job) => {
    try {
      // Create Application in "applied" or "interested"
      await createApplication({
        job_id: job.id,
        status: "interested",
        notes: "Added from Opportunities Board"
      });
      setApplicationCreated(job.id);
      setTimeout(() => setApplicationCreated(null), 3000);
    } catch (e) {
      console.error(e);
      alert("Failed to track application.");
    }
  };

  const handleGenerateOutreach = async (contact: Contact) => {
    setGeneratingOutreachFor(contact.id);
    try {
      await generateOutreach(contact.id, "cold_email");
      alert(`Outreach draft generated successfully! Go to the Outreach Center to customize.`);
    } catch (e) {
      console.error(e);
      alert("Failed to generate outreach draft.");
    } finally {
      setGeneratingOutreachFor(null);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 75) return "var(--score-high)";
    if (score >= 50) return "var(--score-medium)";
    return "var(--score-low)";
  };

  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <div>
          <h1>Discovered Opportunities</h1>
          <p>Browse through jobs crawled from YC Jobs and matched automatically.</p>
        </div>
      </div>

      {/* Filters Toolbar */}
      <div className={styles.filterBar}>
        <div className={styles.searchBox}>
          <Search size={18} className={styles.searchIcon} />
          <input 
            type="text" 
            placeholder="Search by title, role or company..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className={styles.filterGroup}>
          <span className={styles.filterLabel}>Min Match:</span>
          <button 
            className={`${styles.filterBtn} ${minMatch === 0 ? styles.activeFilter : ""}`}
            onClick={() => setMinMatch(0)}
          >
            All
          </button>
          <button 
            className={`${styles.filterBtn} ${minMatch === 50 ? styles.activeFilter : ""}`}
            onClick={() => setMinMatch(50)}
          >
            50%+ Match
          </button>
          <button 
            className={`${styles.filterBtn} ${minMatch === 75 ? styles.activeFilter : ""}`}
            onClick={() => setMinMatch(75)}
          >
            75%+ Match
          </button>
        </div>
      </div>

      <div className={styles.mainLayout}>
        {/* Left Side: Jobs List */}
        <div className={styles.jobsList}>
          {filteredJobs.length === 0 ? (
            <div className={styles.noJobs}>
              <Search size={48} className={styles.emptyIcon} />
              <h3>No jobs match your filters</h3>
              <p>Try clearing your search query or uploading a resume with more keywords.</p>
            </div>
          ) : (
            filteredJobs.map((job) => {
              const score = Math.round(job.match_score || 0);
              const isSelected = selectedJob?.id === job.id;
              const isAlreadyTracked = applications.some(app => app.job_id === job.id);
              
              return (
                <div 
                  key={job.id} 
                  className={`${styles.jobCard} ${isSelected ? styles.selectedCard : ""}`}
                  onClick={() => setSelectedJob(job)}
                >
                  <div className={styles.jobCardMain}>
                    <div className={styles.jobMeta}>
                      <h3>{job.title}</h3>
                      <h4>{job.company}</h4>
                      
                      <div className={styles.metaRow}>
                        <span className={styles.metaItem}>
                          <MapPin size={14} />
                          <span>{job.location}</span>
                        </span>
                        {job.remote && (
                          <span className={`${styles.metaItem} ${styles.remoteTag}`}>
                            Remote Friendly
                          </span>
                        )}
                        <span className={styles.metaItem}>
                          <Layers size={14} />
                          <span>{job.source}</span>
                        </span>
                      </div>
                    </div>

                    <div className={styles.jobScoreBox}>
                      <div 
                        className={styles.scoreCircle}
                        style={{ 
                          borderColor: getScoreColor(score),
                          boxShadow: `0 0 10px ${getScoreColor(score)}40`
                        }}
                      >
                        <span className={styles.scoreNum}>{score}%</span>
                        <span className={styles.scoreLabel}>Match</span>
                      </div>
                    </div>
                  </div>

                  <div className={styles.jobCardFooter}>
                    <div className={styles.skillsTags}>
                      {job.skills_required.slice(0, 4).map(skill => (
                        <span key={skill} className={styles.skillTag}>{skill}</span>
                      ))}
                    </div>

                    <div className={styles.cardActions} onClick={e => e.stopPropagation()}>
                      <button 
                        className={isAlreadyTracked ? "btn-secondary" : "btn-primary"}
                        onClick={() => handleTrackJob(job)}
                        disabled={isAlreadyTracked || applicationCreated === job.id}
                        style={{ padding: "0.4rem 0.8rem", fontSize: "0.8rem" }}
                      >
                        <CheckCircle size={14} />
                        <span>
                          {isAlreadyTracked 
                            ? "Tracked" 
                            : applicationCreated === job.id 
                              ? "Saved!" 
                              : "Track Job"}
                        </span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Side: Detail Drawer */}
        <div className={styles.detailsPanel}>
          {selectedJob ? (
            <div className={styles.detailContainer}>
              <div className={styles.detailHeader}>
                <div>
                  <span className={styles.detailCompany}>{selectedJob.company}</span>
                  <h2>{selectedJob.title}</h2>
                  <p className={styles.detailLoc}>{selectedJob.location} &bull; {selectedJob.remote ? "Remote" : "On-site"}</p>
                </div>
                <a 
                  href={selectedJob.source_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className={styles.extLink}
                >
                  <span>View Original</span>
                  <ExternalLink size={14} />
                </a>
              </div>

              {/* Match Score Breakdown */}
              <div className={styles.breakdownSection}>
                <h3>AI Match Analysis</h3>
                <div className={styles.breakdownMetrics}>
                  {selectedJob.match_explanation?.components ? (
                    Object.entries(selectedJob.match_explanation.components).map(([k, val]: [string, any]) => (
                      <div key={k} className={styles.metricRow}>
                        <span className={styles.metricName}>{k.replace("_", " ")}</span>
                        <div className={styles.metricBarBg}>
                          <div 
                            className={styles.metricBarFill}
                            style={{ 
                              width: `${val * 100}%`,
                              background: getScoreColor(val * 100)
                            }}
                          />
                        </div>
                        <span className={styles.metricVal}>{(val * 100).toFixed(0)}%</span>
                      </div>
                    ))
                  ) : (
                    <p className={styles.noExplanation}>No component breakdown available.</p>
                  )}
                </div>

                {selectedJob.match_explanation?.explanation && (
                  <div className={styles.explanationText}>
                    <p><strong>Agent Feedback:</strong> {selectedJob.match_explanation.explanation}</p>
                  </div>
                )}
              </div>

              {/* Networking Contacts */}
              <div className={styles.contactsSection}>
                <div className={styles.contactsHeader}>
                  <Users size={16} />
                  <h3>Networking Contacts</h3>
                </div>

                {loadingContacts ? (
                  <div className={styles.contactsLoading}>
                    <Loader className={styles.spin} size={20} />
                    <span>Searching company directory...</span>
                  </div>
                ) : contacts.length === 0 ? (
                  <div className={styles.noContacts}>
                    <p>No decision makers identified for this company yet.</p>
                  </div>
                ) : (
                  <div className={styles.contactsList}>
                    {contacts.map((contact) => {
                      const existingMessage = messages.find(m => m.contact_id === contact.id);
                      return (
                        <div key={contact.id} className={styles.contactItem}>
                          <div className={styles.contactInfo}>
                            <h4>{contact.name}</h4>
                            <p>{contact.title}</p>
                            {contact.email && (
                              <span className={styles.contactEmail}>
                                {contact.email} ({Math.round((contact.email_confidence || 0) * 100)}% conf)
                              </span>
                            )}
                          </div>

                          {existingMessage ? (
                            <button 
                              className="btn-secondary"
                              onClick={() => router.push("/outreach")}
                              style={{ 
                                padding: "0.3rem 0.6rem", 
                                fontSize: "0.75rem",
                                color: "var(--accent)",
                                borderColor: "var(--accent)"
                              }}
                            >
                              <CheckCircle size={12} />
                              <span>View Draft</span>
                            </button>
                          ) : (
                            <button 
                              className="btn-secondary"
                              onClick={() => handleGenerateOutreach(contact)}
                              disabled={generatingOutreachFor === contact.id}
                              style={{ padding: "0.3rem 0.6rem", fontSize: "0.75rem" }}
                            >
                              {generatingOutreachFor === contact.id ? (
                                <Loader size={12} className={styles.spin} />
                              ) : (
                                <Mail size={12} />
                              )}
                              <span>Email Draft</span>
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Job Description Text */}
              <div className={styles.descriptionSection}>
                <h3>Full Job Description</h3>
                <div className={styles.descriptionText}>
                  {selectedJob.description}
                </div>
              </div>
            </div>
          ) : (
            <div className={styles.noSelection}>
              <Sparkles size={48} className={styles.sparkleIcon} />
              <h3>Select a job listing</h3>
              <p>Click on any job card to view detailed match explanations, recruiter profiles, and targeted outreach tools.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobsPage;
