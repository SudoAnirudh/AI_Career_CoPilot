"use client";

import React from "react";
import { useApp } from "../../context/AppContext";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle,
  Award,
  Calendar,
  Layers,
  Percent,
  RefreshCw
} from "lucide-react";
import styles from "./page.module.css";

const AnalyticsPage: React.FC = () => {
  const { 
    analyticsSummary, 
    funnelAnalytics, 
    skillGaps, 
    weeklySummary,
    loading,
    refreshAll
  } = useApp();

  const getPercentage = (count: number, total: number) => {
    if (total === 0) return 0;
    return Math.round((count / total) * 100);
  };

  const getStageColor = (stage: string) => {
    switch (stage.toLowerCase()) {
      case "interested": return "#60a5fa";
      case "applied": return "#818cf8";
      case "interviewing": return "#fbbf24";
      case "offer": return "#34d399";
      case "rejected": return "#f87171";
      default: return "var(--color-primary)";
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <div>
          <h1>Search Analytics</h1>
          <p>Detailed performance reports, application funnel conversions, and optimization advice.</p>
        </div>
        <button className="btn-secondary" onClick={refreshAll} disabled={loading}>
          <RefreshCw size={14} className={loading ? styles.spin : ""} />
          <span>Sync Data</span>
        </button>
      </div>

      {/* Top row: Summary widgets */}
      <section className={styles.summaryGrid}>
        <div className={styles.card}>
          <div className={styles.widgetHeader}>
            <Percent size={18} className={styles.cyanIcon} />
            <h4>Average Match Score</h4>
          </div>
          <div className={styles.widgetBody}>
            <h2>{analyticsSummary?.avg_match_score || 0}%</h2>
            <p className={styles.positive}>
              <TrendingUp size={12} />
              <span>Above developer average</span>
            </p>
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.widgetHeader}>
            <Award size={18} className={styles.purpleIcon} />
            <h4>High Match Ratio</h4>
          </div>
          <div className={styles.widgetBody}>
            <h2>{analyticsSummary?.high_match_ratio ? Math.round(analyticsSummary.high_match_ratio * 100) : 0}%</h2>
            <p>Percentage of jobs above 75% Match</p>
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.widgetHeader}>
            <Layers size={18} className={styles.emeraldIcon} />
            <h4>Conversion Rate</h4>
          </div>
          <div className={styles.widgetBody}>
            <h2>
              {getPercentage(
                funnelAnalytics.find(f => f.stage === "interviewing")?.count || 0,
                funnelAnalytics.find(f => f.stage === "applied")?.count || 1
              )}%
            </h2>
            <p>Applied to Interview conversion</p>
          </div>
        </div>
      </section>

      {/* Split section: Funnel vs Skill Gaps */}
      <div className={styles.splitSection}>
        {/* Funnel chart card */}
        <section className={styles.funnelCard}>
          <h3>Application Funnel Stage Distribution</h3>
          <p className={styles.sectionSubtitle}>Total conversion stats across tracked roles</p>
          
          <div className={styles.funnelBars}>
            {funnelAnalytics.length === 0 ? (
              <div className={styles.emptyChart}>
                <p>Add jobs to your Kanban tracking board to see conversion analysis.</p>
              </div>
            ) : (
              funnelAnalytics.map((stageItem) => {
                const maxCount = Math.max(...funnelAnalytics.map(f => f.count), 1);
                const percentWidth = (stageItem.count / maxCount) * 100;
                
                return (
                  <div key={stageItem.stage} className={styles.funnelRow}>
                    <div className={styles.stageLabel}>
                      <span className={styles.stageName}>{stageItem.stage}</span>
                      <span className={styles.stageCount}>{stageItem.count} jobs</span>
                    </div>
                    <div className={styles.barContainer}>
                      <div 
                        className={styles.barFill} 
                        style={{ 
                          width: `${percentWidth}%`,
                          backgroundColor: getStageColor(stageItem.stage),
                          boxShadow: `0 0 10px ${getStageColor(stageItem.stage)}50`
                        }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </section>

        {/* Skill gaps distribution list */}
        <section className={styles.skillsCard}>
          <h3>Market Skills Gaps</h3>
          <p className={styles.sectionSubtitle}>Missing keywords in high demand from your targeted jobs</p>

          <div className={styles.skillsDistribution}>
            {skillGaps.length === 0 ? (
              <div className={styles.emptyChart}>
                <p>No skill gaps identified. Keep parsing resumes and fetching jobs!</p>
              </div>
            ) : (
              <div className={styles.gapsList}>
                {skillGaps.map((gap) => (
                  <div key={gap.skill} className={styles.gapRow}>
                    <div className={styles.gapInfo}>
                      <span className={styles.gapTitle}>{gap.skill}</span>
                      <span className={styles.gapBadge}>Demand: {gap.frequency} postings</span>
                    </div>
                    <div className={styles.gapBarBg}>
                      <div 
                        className={styles.gapBarFill}
                        style={{ width: `${Math.min(gap.frequency * 25, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>

      {/* Weekly Report & Recommendations Card */}
      <section className={styles.reportCard}>
        <div className={styles.reportHeader}>
          <Calendar size={18} />
          <h3>Weekly Advisor Report &amp; Strategy Guidelines</h3>
        </div>
        
        {weeklySummary ? (
          <div className={styles.reportContent}>
            <div className={styles.adviceBox}>
              <h4>🎯 Recommended Strategy Focus</h4>
              <p>{weeklySummary.strategic_focus || "No feedback generated yet. Sync your jobs list to update."}</p>
            </div>

            <div className={styles.analysisGrid}>
              <div className={styles.analysisCol}>
                <h5>💪 Key Strengths Registered</h5>
                <ul>
                  {(weeklySummary.strengths || ["Robust backend architectures", "System performance enhancements"]).map((s: string) => (
                    <li key={s}>{s}</li>
                  ))}
                </ul>
              </div>

              <div className={styles.analysisCol}>
                <h5>⚠️ Identified Weakness Vulnerabilities</h5>
                <ul>
                  {(weeklySummary.weaknesses || ["Lacks specific cloud provider certifications (AWS/GCP)", "Limited testing framework references"]).map((w: string) => (
                    <li key={w} className={styles.warnItem}>
                      <AlertTriangle size={12} />
                      <span>{w}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div className={styles.reportLoading}>
            <p>Upload a parsed resume and scan for jobs to trigger your weekly advisor report.</p>
          </div>
        )}
      </section>
    </div>
  );
};

export default AnalyticsPage;
