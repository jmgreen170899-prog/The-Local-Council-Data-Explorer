/**
 * BinPanel component.
 *
 * Displays bin collection information for a given address.
 * Includes loading states, error handling, and a bar chart for upcoming collections.
 */

import React, { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { BinCollectionResponse } from "./types";
import Card from "../../components/Card";

interface BinPanelProps {
  data: BinCollectionResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

interface ChartDataItem {
  type: string;
  daysUntil: number;
  date: string;
}

const BIN_COLORS: Record<string, string> = {
  Refuse: "#4a5568",
  Recycling: "#48bb78",
  Garden: "#68d391",
  Food: "#f6ad55",
  Glass: "#63b3ed",
  default: "#a0aec0",
};

function getBinColor(type: string): string {
  const normalizedType = type.toLowerCase();
  for (const [key, color] of Object.entries(BIN_COLORS)) {
    if (normalizedType.includes(key.toLowerCase())) {
      return color;
    }
  }
  return BIN_COLORS.default;
}

function getDaysUntil(dateString: string): number {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const targetDate = new Date(dateString);
  targetDate.setHours(0, 0, 0, 0);
  const diffTime = targetDate.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

export function BinPanel({
  data,
  loading,
  error,
  onRetry,
}: BinPanelProps): React.ReactElement {
  const chartData = useMemo<ChartDataItem[]>(() => {
    if (!data?.bins) return [];
    return data.bins
      .map((bin) => ({
        type: bin.type,
        daysUntil: getDaysUntil(bin.collection_date),
        date: formatDate(bin.collection_date),
      }))
      .sort((a, b) => a.daysUntil - b.daysUntil);
  }, [data]);

  if (loading) {
    return (
      <Card title="Bin Collections" className="bin-panel">
        <div className="loading-state">
          <div className="spinner" />
          <p>Loading bin collection data...</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Bin Collections" className="bin-panel">
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
      <Card title="Bin Collections" className="bin-panel">
        <div className="empty-state">
          <p>Enter a postcode or UPRN to view bin collection schedules.</p>
        </div>
      </Card>
    );
  }

  return (
    <Card title="Bin Collections" className="bin-panel">
      <div className="panel-header">
        <p className="address">{data.address}</p>
        <p className="council">{data.council}</p>
      </div>

      {chartData.length > 0 && (
        <div className="chart-section">
          <h4>Days Until Collection</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
            >
              <XAxis type="number" domain={[0, "auto"]} />
              <YAxis type="category" dataKey="type" width={70} />
              <Tooltip
                formatter={(value: number) => [`${value} days`, "Days until"]}
                labelFormatter={(label: string) => label}
              />
              <Bar dataKey="daysUntil" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBinColor(entry.type)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="collection-list">
        <h4>Upcoming Collections</h4>
        <ul>
          {data.bins.map((bin) => {
            const daysUntil = getDaysUntil(bin.collection_date);
            const isToday = daysUntil === 0;
            const isTomorrow = daysUntil === 1;
            return (
              <li key={`${bin.type}-${bin.collection_date}`} className="bin-item">
                <span
                  className="bin-type"
                  style={{ color: getBinColor(bin.type) }}
                >
                  {bin.type}
                </span>
                <span className="bin-date">
                  {formatDate(bin.collection_date)}
                  {isToday && <span className="badge today">Today</span>}
                  {isTomorrow && <span className="badge tomorrow">Tomorrow</span>}
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </Card>
  );
}

export default BinPanel;

