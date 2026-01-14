"""Web Frontend - React/Next.js starter template and architecture."""

import json

NEXTJS_PACKAGE_JSON = {
    "name": "suresh-ai-web",
    "version": "1.0.0",
    "description": "SURESH AI ORIGIN Web Client",
    "scripts": {
        "dev": "next dev",
        "build": "next build",
        "start": "next start",
        "lint": "eslint .",
        "type-check": "tsc --noEmit"
    },
    "dependencies": {
        "next": "^14.0.0",
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "@suresh-ai/sdk": "^2.0.0",
        "axios": "^1.4.0",
        "zustand": "^4.3.0",
        "react-query": "^3.39.0",
        "tailwindcss": "^3.3.0",
        "typescript": "^5.0.0"
    }
}

FRONTEND_STRUCTURE = """
# Next.js Web Client Structure

web-client/
├── pages/
│   ├── _app.tsx              # App wrapper, global state
│   ├── index.tsx             # Home page
│   ├── auth/
│   │   ├── login.tsx
│   │   ├── signup.tsx
│   │   └── sso.tsx
│   ├── dashboard/
│   │   ├── index.tsx         # Main dashboard
│   │   ├── content/
│   │   │   ├── generate.tsx
│   │   │   ├── library.tsx
│   │   │   └── [id].tsx
│   │   ├── campaigns/
│   │   │   ├── index.tsx
│   │   │   ├── create.tsx
│   │   │   └── [id].tsx
│   │   ├── analytics/
│   │   │   ├── revenue.tsx
│   │   │   ├── usage.tsx
│   │   │   └── cohorts.tsx
│   │   └── settings/
│   │       ├── profile.tsx
│   │       ├── billing.tsx
│   │       ├── integrations.tsx
│   │       └── team.tsx
│   ├── api/
│   │   ├── auth/[...nextauth].ts
│   │   ├── proxy/[...proxy].ts
│   ├── 404.tsx
│   └── 500.tsx
│
├── components/
│   ├── common/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Layout.tsx
│   │   └── LoadingSpinner.tsx
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── SignupForm.tsx
│   │   └── ProtectedRoute.tsx
│   ├── content/
│   │   ├── ContentGenerator.tsx
│   │   ├── ContentCard.tsx
│   │   └── ContentLibrary.tsx
│   ├── campaigns/
│   │   ├── CampaignForm.tsx
│   │   ├── CampaignList.tsx
│   │   └── CampaignAnalytics.tsx
│   ├── analytics/
│   │   ├── RevenueChart.tsx
│   │   ├── UsageMetrics.tsx
│   │   └── CohortTable.tsx
│   └── settings/
│       ├── ProfileForm.tsx
│       ├── BillingSettings.tsx
│       └── TeamManagement.tsx
│
├── lib/
│   ├── api.ts                # API client wrapper
│   ├── auth.ts               # Auth logic
│   ├── hooks.ts              # Custom React hooks
│   ├── store.ts              # Zustand store
│   └── utils.ts              # Helper functions
│
├── styles/
│   ├── globals.css
│   └── tailwind.config.js
│
├── public/
│   └── assets/
│
├── .env.local.example
├── tsconfig.json
├── next.config.js
├── tailwind.config.js
└── package.json
"""

API_CLIENT_EXAMPLE = """
// lib/api.ts
import { SureshAIClient } from '@suresh-ai/sdk';

export const apiClient = new SureshAIClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  apiVersion: 'v2'
});

// Auth methods
export const auth = {
  login: (email: string, password: string) =>
    apiClient.auth.login(email, password),
  
  signup: (email: string, password: string, name: string) =>
    apiClient.auth.signup(email, password, name),
  
  logout: () => apiClient.auth.logout(),
};

// Content generation
export const content = {
  generate: (prompt: string, templateId: string) =>
    apiClient.content.generate({ prompt, templateId }),
  
  list: () => apiClient.content.listPrompts(),
  
  get: (id: string) => apiClient.content.get(id),
};

// Campaigns
export const campaigns = {
  create: (data: any) =>
    fetch('/api/campaigns', { method: 'POST', body: JSON.stringify(data) }),
  
  send: (id: string) =>
    fetch(`/api/campaigns/${id}/send`, { method: 'POST' }),
  
  analytics: (id: string) =>
    fetch(`/api/campaigns/${id}/analytics`),
};

// Analytics
export const analytics = {
  revenue: () => fetch('/api/admin/analytics-dashboard'),
  usage: () => fetch('/api/billing/usage'),
};
"""

STORE_EXAMPLE = """
// lib/store.ts
import create from 'zustand';

interface AppState {
  user: any | null;
  token: string | null;
  tier: string;
  setUser: (user: any) => void;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  token: null,
  tier: 'free',
  
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  logout: () => set({ user: null, token: null }),
}));
"""

COMPONENT_EXAMPLE = """
// components/content/ContentGenerator.tsx
import { useState } from 'react';
import { content } from '@/lib/api';

export const ContentGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [template, setTemplate] = useState('blog_post');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await content.generate(prompt, template);
      setResult(response.content);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Content Generator</h1>
      
      <div className="space-y-4">
        <textarea
          className="w-full p-3 border rounded-lg"
          placeholder="Enter your prompt..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={4}
        />
        
        <select
          className="w-full p-2 border rounded-lg"
          value={template}
          onChange={(e) => setTemplate(e.target.value)}
        >
          <option value="blog_post">Blog Post</option>
          <option value="product_description">Product Description</option>
          <option value="email">Email</option>
        </select>
        
        <button
          className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700"
          onClick={handleGenerate}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate Content'}
        </button>
      </div>

      {result && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-2">Generated Content:</p>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
};
"""

print("Next.js frontend structure created")
print(f"Package.json: {json.dumps(NEXTJS_PACKAGE_JSON, indent=2)}")
