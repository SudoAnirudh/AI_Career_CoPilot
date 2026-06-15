"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useApp } from "../context/AppContext";
import { 
  Sparkles, 
  Briefcase, 
  Trophy, 
  Mail, 
  ArrowUpRight, 
  CheckCircle,
  FileText, 
  HelpCircle
} from "lucide-react";
import styles from "./page.module.css";

const Dashboard: React.FC = () => {
  const { 
    jobs, 
    applications, 
    messages, 
    activeProfile, 
    skillGaps,
    discoverJobs,
    discovering
  } = useApp();

  const [discoveryStarted, setDiscoveryStarted] = useState(false);

  // Statistics
  const totalDiscovered = jobs.length;
  const highMatches = jobs.filter(j => (j.match_score || 0) >= 75).length;
  const activeApplications = applications.filter(a => a.status !== "rejected" && a.status !== "offer").length;
  const sentOutreach = messages.filter(m => m.status === "sent").length;

  const handleDiscover = async () => {
    setDiscoveryStarted(true);
    try {
      await discoverJobs();
    } catch (e) {
      console.error(e);
    } finally {
      setDiscoveryStarted(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Overview Stats Cards */}
      <section className={styles.statsGrid}>
        <div className={`${styles.card} animate-slideup`} style={{ animationDelay: "0.05s" }}>
          <div className={styles.cardHeader}>
            <span className={`${styles.iconWrapper} ${styles.blue}`}>
              <Briefcase size={20} />
            </span>
            <span className={styles.cardGrowth}>+12 new today</span>
          </div>
          <div className={styles.cardBody}>
            <h3>{totalDiscovered}</h3>
            <p>Discovered Jobs</p>
          </div>
        </div>

        <div className={`${styles.card} animate-slideup`} style={{ animationDelay: "0.1s" }}>
          <div className={styles.cardHeader}>
            <span className={`${styles.iconWrapper} ${styles.purple}`}>
              <Sparkles size={20} />
            </span>
            <span className={styles.cardGrowth}>{((highMatches / (totalDiscovered || 1)) * 100).toFixed(0)}% rate</span>
          </div>
          <div className={styles.cardBody}>
            <h3>{highMatches}</h3>
            <p>High Match Ratio (&gt;75%)</p>
          </div>
        </div>

        <div className={`${styles.card} animate-slideup`} style={{ animationDelay: "0.15s" }}>
          <div className={styles.cardHeader}>
            <span className={`${styles.iconWrapper} ${styles.green}`}>
              <Trophy size={20} />
            </span>
            <span className={styles.cardGrowth}>Active tracking</span>
          </div>
          <div className={styles.cardBody}>
            <h3>{activeApplications}</h3>
            <p>Active Applications</p>
          </div>
        </div>

        <div className={`${styles.card} animate-slideup`} style={{ animationDelay: "0.20s" }}>
          <div className={styles.cardHeader}>
            <span className={`${styles.iconWrapper} ${styles.pink}`}>
              <Mail size={20} />
            </span>
            <span className={styles.cardGrowth}>Replies expected</span>
          </div>
          <div className={styles.cardBody}>
            <h3>{sentOutreach}</h3>
            <p>Outreach Sent</p>
          </div>
        </div>
      </section>

      {/* Main Content Split Section */}
      <div className={styles.splitSection}>
        {/* Left Side: Latest Match Recommendations */}
        <section className={styles.leftPanel}>
          <div className={styles.panelHeader}>
            <div>
              <h2>Recommended Opportunities</h2>
              <p>Top AI-matched jobs aligned to your parsed skills.</p>
            </div>
            <button 
              className="btn-primary" 
              onClick={handleDiscover}
              disabled={discovering || discoveryStarted}
            >
              <Sparkles size={16} />
              <span>{discovering || discoveryStarted ? "Scanning..." : "Scan for Jobs"}</span>
            </button>
          </div>

          <div className={styles.jobsList}>
            {jobs.length === 0 ? (
              <div className={styles.emptyState}>
                <Briefcase size={48} className={styles.emptyIcon} />
                <h3>No jobs found yet</h3>
                <p>Upload your resume first, then click "Scan for Jobs" to spin up discovery agents.</p>
              </div>
            ) : (
              jobs.slice(0, 4).map((job) => {
                const isHighMatch = (job.match_score || 0) >= 75;
                const scoreColor = isHighMatch ? "var(--score-high)" : "var(--score-medium)";
                return (
                  <div key={job.id} className={styles.jobItem}>
                    <div className={styles.jobInfo}>
                      <h4>{job.title}</h4>
                      <p>{job.company} &bull; {job.location}</p>
                      <div className={styles.tags}>
                        {job.skills_required.slice(0, 3).map((skill) => (
                          <span key={skill} className={styles.tag}>{skill}</span>
                        ))}
                      </div>
                    </div>
                    
                    <div className={styles.jobActions}>
                      <div 
                        className={styles.matchBadge}
                        style={{ borderColor: scoreColor, color: scoreColor }}
                      >
                        {Math.round(job.match_score || 0)}% Match
                      </div>
                      <Link href={`/jobs`} className={styles.viewLink}>
                        <span>Explore</span>
                        <ArrowUpRight size={14} />
                      </Link>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </section>

        {/* Right Side: Skill Gaps and Resume Analytics */}
        <section className={styles.rightPanel}>
          <div className={styles.panelHeader}>
            <div>
              <h2>Skill Gaps Identified</h2>
              <p>Keywords missing from your resume vs. target jobs.</p>
            </div>
          </div>

          <div className={styles.skillsList}>
            {!activeProfile ? (
              <div className={styles.emptyState}>
                <FileText size={48} className={styles.emptyIcon} />
                <h3>Resume not parsed</h3>
                <p>Upload a PDF resume in the top header to analyze skill gaps automatically.</p>
              </div>
            ) : skillGaps.length === 0 ? (
              <div className={styles.perfectMatch}>
                <CheckCircle size={36} className={styles.checkIcon} />
                <h3>Perfect Match Profile</h3>
                <p>Your resume matches all identified skills for your targeted roles!</p>
              </div>
            ) : (
              <div className={styles.gapsGrid}>
                {skillGaps.slice(0, 6).map((gap) => (
                  <div key={gap.skill} className={styles.gapCard}>
                    <div className={styles.gapHeader}>
                      <span className={styles.gapName}>{gap.skill}</span>
                      <span className={styles.gapCount}>{gap.frequency} jobs</span>
                    </div>
                    <div className={styles.gapProgressContainer}>
                      <div 
                        className={styles.gapProgressBar} 
                        style={{ width: `${Math.min(gap.frequency * 25, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
                <div className={styles.resumeOptimizeBanner}>
                  <p>Add these keywords to your resume to increase match rates by up to 30%.</p>
                  <Link href="/settings" className="btn-secondary" style={{ width: "100%", justifyContent: "center", marginTop: "0.5rem" }}>
                    Optimize Resume
                  </Link>
                </div>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
