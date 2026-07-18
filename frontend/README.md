# 🎨 AI Career CoPilot - Next.js Client Dashboard

The frontend is a modern client built using **Next.js (App Router)** and **React 19**. It connects to the FastAPI backend services over HTTP and WebSockets, rendering dashboards, tracking job pipelines via Kanban, and exposing tailored outreach drafts.

---

## 📂 Frontend Directory Structure

```
frontend/
├── public/                 # Static asset directories (images, SVGs)
├── src/
│   ├── app/                # Next.js App Router Page layouts
│   │   ├── analytics/      # Application funnel metrics & skill gap charts
│   │   ├── jobs/           # Feed of discovered & scored job postings
│   │   ├── kanban/         # Kanban pipeline board for applications status
│   │   ├── outreach/       # Contact profiles listing & email outreach generator
│   │   ├── settings/       # Profile details & API key configurations
│   │   ├── globals.css     # CSS style entrypoint & Tailwind configurations
│   │   ├── layout.tsx      # Main layout template containing navigation shell
│   │   └── page.tsx        # Homepage dashboard entrypoint
│   ├── components/         # Reusable design system UI components
│   ├── context/            # React global context providers
│   └── firebase.ts         # Firebase client config
├── Dockerfile              # Production Node container compiler script
└── package.json            # NPM package dependencies and scripts
```

---

## 🚀 Key Routes & Pages

1.  **Dashboard Home (`/`)**: Main command center showing total jobs discovered, active applications, resume parsing status indicators, and quick action buttons.
2.  **Jobs Center (`/jobs`)**: Feeds in scraped listings, displaying detailed match scores (e.g. `85% Match`) and a breakdown of skills overlap, matching projects, and location details.
3.  **Kanban pipeline (`/kanban`)**: Drag-and-drop board mapping candidate states: `Discovered` ➔ `Saved` ➔ `Applied` ➔ `Interviewing` ➔ `Offered` ➔ `Rejected`.
4.  **Outreach (`/outreach`)**: Displays researched company team members (recruiters/engineering managers) along with AI-generated cold email and LinkedIn message drafts.
5.  **Analytics (`/analytics`)**: Renders Recharts funnel progress and a detailed summary of missing skills frequently requested by the job listings.

---

## 💻 Local Setup & Commands

### 1. Configure Environmental Variables
Create a `.env.local` inside the `frontend/` directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### 2. Install & Start Development Server
```bash
npm install
npm run dev
```
Open `http://localhost:3000` to access the dashboard.

### 3. Build & Compile for Production
```bash
npm run build
npm start
```
