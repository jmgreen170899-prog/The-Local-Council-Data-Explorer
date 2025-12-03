# Frontend Structure

> A detailed guide to the React/TypeScript frontend architecture, component organization, and development patterns.

---

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Architecture Patterns](#architecture-patterns)
- [Components](#components)
- [Features](#features)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [Styling](#styling)
- [Development](#development)
- [Best Practices](#best-practices)

---

## Overview

The frontend is built with **React 19** and **TypeScript**, using a feature-based architecture that promotes modularity and maintainability.

### Key Characteristics

| Feature | Implementation |
|---------|----------------|
| **Framework** | React 19 with hooks |
| **Language** | TypeScript 5.9+ (strict mode) |
| **Build Tool** | Vite for fast development |
| **Charting** | Recharts for data visualization |
| **Styling** | CSS with responsive design |
| **State** | Custom hooks for async state |

---

## Directory Structure

```
frontend/
├── src/
│   ├── main.tsx                # Application bootstrap
│   ├── App.tsx                 # Root component with routing
│   ├── App.css                 # Global and component styles
│   ├── index.css               # Base styles and resets
│   ├── vite-env.d.ts           # Vite type definitions
│   │
│   ├── api/                    # API client configuration
│   │   └── client.ts           # Centralized API config
│   │
│   ├── components/             # Shared UI components
│   │   ├── Layout.tsx          # Page layout with navigation
│   │   ├── Card.tsx            # Container component
│   │   └── ChartWrapper.tsx    # Chart display wrapper
│   │
│   ├── features/               # Feature modules
│   │   ├── bins/               # Bin collections feature
│   │   │   ├── BinPanel.tsx    # Main panel component
│   │   │   ├── api.ts          # API functions
│   │   │   └── types.ts        # TypeScript types
│   │   │
│   │   ├── planning/           # Planning applications feature
│   │   │   ├── PlanningPanel.tsx
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   │
│   │   └── air/                # Air quality feature
│   │       ├── AirQualityPanel.tsx
│   │       ├── api.ts
│   │       └── types.ts
│   │
│   ├── hooks/                  # Custom React hooks
│   │   └── useApi.ts           # Async data fetching hook
│   │
│   └── assets/                 # Static assets
│
├── public/                     # Static files (served as-is)
├── index.html                  # HTML entry point
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
├── tsconfig.app.json           # App-specific TS config
├── tsconfig.node.json          # Node-specific TS config
├── eslint.config.js            # ESLint configuration
├── package.json                # Dependencies and scripts
├── Dockerfile                  # Container build instructions
└── nginx.conf                  # Production nginx config
```

---

## Architecture Patterns

### Feature-Based Architecture

Each feature is self-contained with its own:

- **Panel Component** - Main UI for the feature
- **API Module** - HTTP functions with retry logic
- **Types Module** - TypeScript interfaces

```
features/
├── bins/
│   ├── BinPanel.tsx      # UI component
│   ├── api.ts            # Data fetching
│   └── types.ts          # Type definitions
├── planning/
│   ├── PlanningPanel.tsx
│   ├── api.ts
│   └── types.ts
└── air/
    ├── AirQualityPanel.tsx
    ├── api.ts
    └── types.ts
```

### Benefits

1. **Cohesion**: Related code lives together
2. **Scalability**: Add features without touching existing code
3. **Maintainability**: Clear ownership of each module
4. **Testing**: Feature modules can be tested in isolation

---

## Components

### Shared Components

#### `Layout.tsx`

Main application layout with navigation:

```typescript
interface LayoutProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  children: React.ReactNode;
}

export type TabId = "bins" | "planning" | "air";

export default function Layout({ activeTab, onTabChange, children }: LayoutProps) {
  return (
    <div className="layout">
      <header className="layout-header">
        <h1>Local Council Data Explorer</h1>
        <nav className="layout-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`nav-tab ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => onTabChange(tab.id)}
            >
              <span className="nav-icon">{tab.icon}</span>
              <span className="nav-label">{tab.label}</span>
            </button>
          ))}
        </nav>
      </header>
      <main className="layout-main">{children}</main>
      <footer className="layout-footer">
        <p>Local Council Data Explorer</p>
      </footer>
    </div>
  );
}
```

#### `Card.tsx`

Reusable container component:

```typescript
interface CardProps {
  title?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export default function Card({ title, children, actions }: CardProps) {
  return (
    <div className="card">
      {title && (
        <div className="card-header">
          <h3 className="card-title">{title}</h3>
          {actions && <div className="card-actions">{actions}</div>}
        </div>
      )}
      <div className="card-content">{children}</div>
    </div>
  );
}
```

#### `ChartWrapper.tsx`

Responsive chart container:

```typescript
interface ChartWrapperProps {
  children: React.ReactNode;
  height?: number;
}

export default function ChartWrapper({ children, height = 300 }: ChartWrapperProps) {
  return (
    <div className="chart-wrapper" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        {children}
      </ResponsiveContainer>
    </div>
  );
}
```

---

## Features

### Bins Feature

**Purpose**: Display bin collection schedules with countdown visualization

**Components**:

```typescript
// BinPanel.tsx
interface BinPanelProps {
  data: BinCollectionResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

export default function BinPanel({ data, loading, error, onRetry }: BinPanelProps) {
  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={onRetry} />;
  if (!data) return <EmptyState />;

  return (
    <Card title="Bin Collections">
      {/* Header with address and council */}
      <div className="panel-header">
        <p className="address">{data.address}</p>
        <p className="council">{data.council}</p>
      </div>

      {/* Chart showing days until collection */}
      <ChartSection data={data.bins} />

      {/* List of upcoming collections */}
      <CollectionList bins={data.bins} />
    </Card>
  );
}
```

**Types**:

```typescript
// types.ts
export interface BinCollection {
  type: string;
  collection_date: string;
}

export interface BinCollectionResponse {
  address: string;
  council: string;
  bins: BinCollection[];
}
```

### Planning Feature

**Purpose**: Display planning applications with filtering

**Types**:

```typescript
export interface PlanningApplication {
  reference: string;
  address: string;
  proposal: string;
  status: string;
  received_date: string;
  decision_date: string | null;
  decision: string | null;
  applicant_name: string | null;
  application_type: string | null;
}

export interface PlanningResponse {
  lpa: string;
  applications: PlanningApplication[];
  total_count: number;
}
```

### Air Quality Feature

**Purpose**: Display DAQI readings with pollutant breakdown

**Types**:

```typescript
export interface Pollutant {
  name: string;
  value: number;
  units: string;
  band: string | null;
  index: number | null;
}

export interface AirQualityResponse {
  area: string;
  max_daqi: number;
  summary: string;
  pollutants: Pollutant[];
  forecast_date: string | null;
}
```

---

## State Management

### `useApi` Hook

Custom hook for async data fetching with loading, error, and retry:

```typescript
interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends ApiState<T> {
  refetch: () => Promise<void>;
  reset: () => void;
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  dependencies: unknown[] = [],
  immediate: boolean = true
): UseApiReturn<T> {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const result = await fetcher();
      setState({ data: result, loading: false, error: null });
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "An error occurred",
      }));
    }
  }, [fetcher]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [...dependencies, immediate]);

  return {
    ...state,
    refetch: execute,
    reset: () => setState({ data: null, loading: false, error: null }),
  };
}
```

### State Flow

```
User Action (tab change, retry)
        │
        ▼
App Component
├── activeTab state
├── useApi hooks (x3)
│   ├── binsApi
│   ├── planningApi
│   └── airApi
        │
        ▼
Panel Components receive:
├── data: T | null
├── loading: boolean
├── error: string | null
└── onRetry: () => void
```

---

## API Integration

### API Client Configuration

```typescript
// api/client.ts
export const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";
```

### Feature API Functions

Each feature has its own API module:

```typescript
// features/bins/api.ts
import { API_BASE } from "../../api/client";
import type { BinCollectionResponse } from "./types";

export async function fetchBinCollections(
  postcode: string,
  houseNumber?: string
): Promise<BinCollectionResponse> {
  const params = new URLSearchParams();
  params.set("postcode", postcode);
  if (houseNumber) {
    params.set("house_number", houseNumber);
  }

  const response = await fetch(`${API_BASE}/bins?${params.toString()}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
```

### Retry Logic Pattern

```typescript
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

async function fetchWithRetry<T>(url: string): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const response = await fetch(url);
      
      if (response.status >= 500) {
        await delay(RETRY_DELAY * (attempt + 1));
        continue;
      }
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return response.json();
    } catch (err) {
      lastError = err instanceof Error ? err : new Error("Unknown error");
      await delay(RETRY_DELAY * (attempt + 1));
    }
  }

  throw lastError || new Error("Max retries exceeded");
}
```

---

## Styling

### CSS Architecture

```
App.css
├── Layout Styles       (.layout, .layout-header, etc.)
├── Card Styles         (.card, .card-header, etc.)
├── State Styles        (.loading-state, .error-state, .empty-state)
├── Panel Styles        (.panel-header, .summary-chips)
├── Feature Styles
│   ├── Bins            (.bin-item, .bin-type, .bin-date)
│   ├── Planning        (.application-item, .status-badge)
│   └── Air Quality     (.daqi-indicator, .pollutant-grid)
└── Responsive Styles   (@media queries)
```

### Design Tokens

```css
/* Colors */
--primary: #1e3a5f;
--primary-light: #2d5a87;
--text: #2d3748;
--text-muted: #718096;
--border: #e2e8f0;
--background: #f5f7fa;

/* Spacing */
--space-xs: 0.25rem;
--space-sm: 0.5rem;
--space-md: 1rem;
--space-lg: 1.5rem;
--space-xl: 2rem;

/* Border Radius */
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
```

### Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 480px) { ... }

/* Tablet */
@media (max-width: 768px) { ... }

/* Desktop */
@media (min-width: 769px) { ... }
```

---

## Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

### Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

### TypeScript Configuration

```json
// tsconfig.app.json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "jsx": "react-jsx"
  }
}
```

---

## Best Practices

### Component Guidelines

1. **Functional components** - Use hooks, not class components
2. **Props interface** - Define explicit props types
3. **Memoization** - Use `useMemo` and `useCallback` for expensive operations
4. **Error boundaries** - Wrap feature panels for graceful error handling

### TypeScript Guidelines

1. **Strict mode** - Enable all strict checks
2. **Explicit types** - Avoid `any` type
3. **Interface vs Type** - Use interface for objects, type for unions
4. **No implicit returns** - Be explicit about return types

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Component | PascalCase | `BinPanel.tsx` |
| Hook | camelCase with `use` prefix | `useApi.ts` |
| Type/Interface | PascalCase | `BinCollectionResponse` |
| CSS class | kebab-case | `.bin-item` |
| Constant | UPPER_SNAKE_CASE | `API_BASE` |

### Performance Tips

1. **Lazy loading** - Consider code splitting for large features
2. **Virtualization** - Use for long lists
3. **Image optimization** - Use appropriate formats and sizes
4. **Bundle analysis** - Monitor bundle size

---

## Related Documentation

- [Architecture Overview](./ARCHITECTURE_OVERVIEW.md) - High-level system architecture
- [Backend Structure](./BACKEND_STRUCTURE.md) - Backend architecture details
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions
