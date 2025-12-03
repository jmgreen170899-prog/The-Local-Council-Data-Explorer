/**
 * PlanningPanel component.
 *
 * Displays planning application information for a local planning authority.
 * Includes loading states, error handling, and status summary charts.
 */

import React, { useMemo } from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import type { PlanningResponse, PlanningApplication } from "./types";
import Card from "../../components/Card";

interface PlanningPanelProps {
  data: PlanningResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

interface StatusCount {
  status: string;
  count: number;
  [key: string]: string | number;
}

const STATUS_COLORS: Record<string, string> = {
  Pending: "#f6ad55",
  Approved: "#48bb78",
  Refused: "#fc8181",
  Withdrawn: "#a0aec0",
  "Under Consideration": "#63b3ed",
  Registered: "#b794f4",
  default: "#718096",
};

function getStatusColor(status: string): string {
  for (const [key, color] of Object.entries(STATUS_COLORS)) {
    if (status.toLowerCase().includes(key.toLowerCase())) {
      return color;
    }
  }
  return STATUS_COLORS.default;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function PlanningPanel({
  data,
  loading,
  error,
  onRetry,
}: PlanningPanelProps): React.ReactElement {
  const statusCounts = useMemo<StatusCount[]>(() => {
    if (!data?.applications) return [];
    const counts: Record<string, number> = {};
    data.applications.forEach((app) => {
      counts[app.status] = (counts[app.status] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([status, count]) => ({ status, count }))
      .sort((a, b) => b.count - a.count);
  }, [data]);

  if (loading) {
    return (
      <Card title="Planning Applications" className="planning-panel">
        <div className="loading-state">
          <div className="spinner" />
          <p>Loading planning applications...</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Planning Applications" className="planning-panel">
        <div className="error-state">
          <p className="error-message">⚠️ {error}</p>
          <button onClick={onRetry} className="retry-button">
            Retry
          </button>
        </div>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card title="Planning Applications" className="planning-panel">
        <div className="empty-state">
          <p>Enter a Local Planning Authority to view applications.</p>
        </div>
      </Card>
    );
  }

  return (
    <Card title="Planning Applications" className="planning-panel">
      <div className="panel-header">
        <p className="lpa">{data.lpa}</p>
        <div className="summary-chips">
          <span className="chip primary">{data.total_count} Total</span>
          {statusCounts.slice(0, 3).map((item) => (
            <span
              key={item.status}
              className="chip"
              style={{ backgroundColor: getStatusColor(item.status) }}
            >
              {item.count} {item.status}
            </span>
          ))}
        </div>
      </div>

      {statusCounts.length > 0 && (
        <div className="chart-section">
          <h4>Applications by Status</h4>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={statusCounts}
                dataKey="count"
                nameKey="status"
                cx="50%"
                cy="50%"
                outerRadius={70}
                label={({ name, percent }) =>
                  `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`
                }
                labelLine={false}
              >
                {statusCounts.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getStatusColor(entry.status)} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number) => [`${value} applications`, "Count"]}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="application-list">
        <h4>Recent Applications</h4>
        <ul>
          {data.applications.slice(0, 5).map((app: PlanningApplication) => (
            <li key={app.reference} className="application-item">
              <div className="application-header">
                <span className="reference">{app.reference}</span>
                <span
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(app.status) }}
                >
                  {app.status}
                </span>
              </div>
              <p className="proposal">{app.proposal}</p>
              <div className="application-meta">
                <span className="address">{app.address}</span>
                <span className="date">Received: {formatDate(app.received_date)}</span>
                {app.decision && (
                  <span className="decision">Decision: {app.decision}</span>
                )}
              </div>
            </li>
          ))}
        </ul>
        {data.applications.length > 5 && (
          <p className="more-info">
            Showing 5 of {data.applications.length} applications
          </p>
        )}
      </div>
    </Card>
  );
}

export default PlanningPanel;
