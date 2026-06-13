"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { API_BASE_URL, WS_BASE_URL } from "../config";
import { auth, onAuthStateChanged, FirebaseUser } from "../firebase";

export interface Profile {
  id: string;
  version: number;
  raw_text: string;
  skills: any;
  projects: any[];
  education: any[];
  experience: any[];
  certifications: any[];
  resume_url: string;
  is_active: boolean;
  uploaded_at: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  description: string;
  skills_required: string[];
  location: string;
  remote: boolean;
  salary_min?: number;
  salary_max?: number;
  experience_years_min?: number;
  experience_years_max?: number;
  source: string;
  source_url: string;
  match_score?: number;
  match_explanation?: any;
  status: string;
  discovered_at: string;
  posted_date: string;
}

export interface Contact {
  id: string;
  job_id: string;
  name: string;
  title: string;
  company: string;
  linkedin_url?: string;
  email?: string;
  email_confidence?: number;
  connection_degree?: number;
  source: string;
  status: string;
  notes?: string;
}

export interface Message {
  id: string;
  contact_id: string;
  job_id: string;
  type: string;
  draft: string;
  final_text?: string;
  status: string;
  created_at: string;
  sent_at?: string;
  replied_at?: string;
}

export interface Application {
  id: string;
  job_id: string;
  profile_version: number;
  status: string;
  applied_date?: string;
  platform?: string;
  interview_rounds?: any[];
  offer_details?: any;
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface AppContextType {
  activeProfile: Profile | null;
  jobs: Job[];
  applications: Application[];
  messages: Message[];
  analyticsSummary: any;
  funnelAnalytics: any[];
  skillGaps: any[];
  weeklySummary: any;
  user: FirebaseUser | { email: string; displayName: string } | null;
  loading: boolean;
  discovering: boolean;
  uploading: boolean;
  wsStatus: "connected" | "disconnected" | "connecting";
  refreshAll: () => Promise<void>;
  uploadResume: (file: File) => Promise<Profile>;
  syncResumeFromDrive: () => Promise<Profile>;
  discoverJobs: () => Promise<void>;
  saveJob: (jobId: string) => Promise<Job>;
  getContacts: (jobId: string) => Promise<Contact[]>;
  generateOutreach: (contactId: string, type: string) => Promise<Message>;
  sendOutreach: (messageId: string) => Promise<Message>;
  updateMessageDraft: (messageId: string, text: string) => Promise<Message>;
  createApplication: (payload: any) => Promise<Application>;
  updateApplication: (appId: string, payload: any) => Promise<Application>;
  deleteApplication: (appId: string) => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeProfile, setActiveProfile] = useState<Profile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  
  // Analytics
  const [analyticsSummary, setAnalyticsSummary] = useState<any>(null);
  const [funnelAnalytics, setFunnelAnalytics] = useState<any[]>([]);
  const [skillGaps, setSkillGaps] = useState<any[]>([]);
  const [weeklySummary, setWeeklySummary] = useState<any>(null);

  // Loading States
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [uploading, setUploading] = useState(false);

  // Auth (Firebase with mock bypass fallback)
  const [user, setUser] = useState<any>({
    email: "anirudhsudheer@gmail.com",
    displayName: "Anirudh Sudheer"
  });

  const [wsStatus, setWsStatus] = useState<"connected" | "disconnected" | "connecting">("connecting");

  // Get Auth headers
  const getHeaders = useCallback(() => {
    return {
      "Authorization": "Bearer dev_user_clerk", // Bypass developer auth toggle on backend
      "Content-Type": "application/json"
    };
  }, []);

  const refreshAll = useCallback(async () => {
    try {
      const headers = getHeaders();
      
      // Fetch Active Profile
      const profileRes = await fetch(`${API_BASE_URL}/resume/profile`, { headers });
      if (profileRes.ok) {
        const profileData = await profileRes.json();
        setActiveProfile(profileData);
      } else {
        setActiveProfile(null);
      }

      // Fetch Jobs
      const jobsRes = await fetch(`${API_BASE_URL}/jobs`, { headers });
      if (jobsRes.ok) {
        setJobs(await jobsRes.json());
      }

      // Fetch Applications
      const appsRes = await fetch(`${API_BASE_URL}/applications`, { headers });
      if (appsRes.ok) {
        setApplications(await appsRes.json());
      }

      // Fetch Messages
      const msgRes = await fetch(`${API_BASE_URL}/outreach/messages`, { headers });
      if (msgRes.ok) {
        setMessages(await msgRes.json());
      }

      // Fetch Analytics
      const summaryRes = await fetch(`${API_BASE_URL}/analytics/summary`, { headers });
      if (summaryRes.ok) setAnalyticsSummary(await summaryRes.json());
      
      const funnelRes = await fetch(`${API_BASE_URL}/analytics/funnel`, { headers });
      if (funnelRes.ok) {
        const funnelData = await funnelRes.json();
        setFunnelAnalytics(funnelData.stages || []);
      }
      
      const skillGapsRes = await fetch(`${API_BASE_URL}/analytics/skill-gaps`, { headers });
      if (skillGapsRes.ok) setSkillGaps(await skillGapsRes.json());
      
      const weeklyRes = await fetch(`${API_BASE_URL}/analytics/weekly`, { headers });
      if (weeklyRes.ok) setWeeklySummary(await weeklyRes.json());

    } catch (e) {
      console.error("Error fetching state data:", e);
    } finally {
      setLoading(false);
    }
  }, [getHeaders]);

  // Initial authentication listener + initial loading
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser);
      } else {
        // Fall back to default developer profile in dev environment
        setUser({
          email: "anirudhsudheer@gmail.com",
          displayName: "Anirudh Sudheer"
        });
      }
      refreshAll();
    });
    return () => unsubscribe();
  }, [refreshAll]);

  // WebSocket connections for real-time notifications
  useEffect(() => {
    let wsJobs: WebSocket | null = null;
    let wsTasks: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connectWS = () => {
      setWsStatus("connecting");
      
      try {
        wsJobs = new WebSocket(`${WS_BASE_URL}/jobs`);
        wsTasks = new WebSocket(`${WS_BASE_URL}/tasks`);

        wsJobs.onopen = () => {
          setWsStatus("connected");
          console.log("WebSocket connected to /ws/jobs");
        };

        wsJobs.onmessage = (event) => {
          const message = JSON.parse(event.data);
          console.log("Real-time job update:", message);
          // Refresh jobs & summary
          refreshAll();
        };

        wsJobs.onclose = () => {
          setWsStatus("disconnected");
          console.log("WebSocket disconnected from /ws/jobs");
          // Schedule reconnect
          reconnectTimeout = setTimeout(connectWS, 5000);
        };

        wsTasks.onopen = () => {
          console.log("WebSocket connected to /ws/tasks");
        };

        wsTasks.onmessage = (event) => {
          const message = JSON.parse(event.data);
          console.log("Real-time background task update:", message);
          // Refresh state
          refreshAll();
        };

        wsTasks.onclose = () => {
          console.log("WebSocket disconnected from /ws/tasks");
        };
      } catch (err) {
        console.error("WebSocket connection error:", err);
        setWsStatus("disconnected");
        reconnectTimeout = setTimeout(connectWS, 5000);
      }
    };

    connectWS();

    return () => {
      if (wsJobs) wsJobs.close();
      if (wsTasks) wsTasks.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [refreshAll]);

  const uploadResume = async (file: File): Promise<Profile> => {
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const response = await fetch(`${API_BASE_URL}/resume/upload`, {
        method: "POST",
        headers: {
          "Authorization": "Bearer dev_user_clerk"
        },
        body: formData
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to parse resume");
      }
      
      const profile = await response.json();
      setActiveProfile(profile);
      await refreshAll();
      return profile;
    } finally {
      setUploading(false);
    }
  };

  const syncResumeFromDrive = async (): Promise<Profile> => {
    setUploading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/resume/sync/drive`, {
        method: "POST",
        headers: getHeaders()
      });
      if (!response.ok) throw new Error("Sync failed");
      const profile = await response.json();
      setActiveProfile(profile);
      await refreshAll();
      return profile;
    } finally {
      setUploading(false);
    }
  };

  const discoverJobs = async () => {
    setDiscovering(true);
    try {
      const response = await fetch(`${API_BASE_URL}/jobs/discover`, {
        method: "POST",
        headers: getHeaders()
      });
      if (!response.ok) throw new Error("Job discovery request failed");
      await refreshAll();
    } finally {
      setDiscovering(false);
    }
  };

  const saveJob = async (jobId: string): Promise<Job> => {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/save`, {
      method: "POST",
      headers: getHeaders()
    });
    if (!response.ok) throw new Error("Failed to save job");
    const job = await response.json();
    await refreshAll();
    return job;
  };

  const getContacts = async (jobId: string): Promise<Contact[]> => {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/contacts`, {
      headers: getHeaders()
    });
    if (!response.ok) throw new Error("Failed to load contacts");
    return await response.json();
  };

  const generateOutreach = async (contactId: string, type: string): Promise<Message> => {
    const response = await fetch(
      `${API_BASE_URL}/outreach/generate?contact_id=${contactId}&message_type=${type}`,
      {
        method: "POST",
        headers: getHeaders()
      }
    );
    if (!response.ok) throw new Error("Failed to generate outreach");
    const msg = await response.json();
    await refreshAll();
    return msg;
  };

  const sendOutreach = async (messageId: string): Promise<Message> => {
    const response = await fetch(`${API_BASE_URL}/outreach/messages/${messageId}/send`, {
      method: "POST",
      headers: getHeaders()
    });
    if (!response.ok) throw new Error("Failed to send outreach");
    const msg = await response.json();
    await refreshAll();
    return msg;
  };

  const updateMessageDraft = async (messageId: string, text: string): Promise<Message> => {
    const response = await fetch(`${API_BASE_URL}/outreach/messages/${messageId}`, {
      method: "PATCH",
      headers: getHeaders(),
      body: JSON.stringify({ draft: text })
    });
    if (!response.ok) throw new Error("Failed to save draft");
    const msg = await response.json();
    await refreshAll();
    return msg;
  };

  const createApplication = async (payload: any): Promise<Application> => {
    const response = await fetch(`${API_BASE_URL}/applications`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error("Failed to create application");
    const app = await response.json();
    await refreshAll();
    return app;
  };

  const updateApplication = async (appId: string, payload: any): Promise<Application> => {
    const response = await fetch(`${API_BASE_URL}/applications/${appId}`, {
      method: "PATCH",
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error("Failed to update application");
    const app = await response.json();
    await refreshAll();
    return app;
  };

  const deleteApplication = async (appId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/applications/${appId}`, {
      method: "DELETE",
      headers: getHeaders()
    });
    if (!response.ok) throw new Error("Failed to delete application");
    await refreshAll();
  };

  return (
    <AppContext.Provider
      value={{
        activeProfile,
        jobs,
        applications,
        messages,
        analyticsSummary,
        funnelAnalytics,
        skillGaps,
        weeklySummary,
        user,
        loading,
        discovering,
        uploading,
        wsStatus,
        refreshAll,
        uploadResume,
        syncResumeFromDrive,
        discoverJobs,
        saveJob,
        getContacts,
        generateOutreach,
        sendOutreach,
        updateMessageDraft,
        createApplication,
        updateApplication,
        deleteApplication
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
};
