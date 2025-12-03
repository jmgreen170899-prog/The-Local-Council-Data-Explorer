/**
 * AirQualityPanel component.
 *
 * Displays air quality information for a given area.
 * Includes loading states, error handling, and pollutant bar charts.
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
  ReferenceLine,
} from "recharts";
import type { AirQualityResponse, Pollutant } from "./types";
import Card from "../../components/Card";

interface AirQualityPanelProps {
  data: AirQualityResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

interface PollutantChartData {
  name: string;
  value: number;
  units: string;
  index: number | null;
  [key: string]: string | number | null;
}

const DAQI_COLORS: Record<string, string> = {
  Low: "#48bb78",
  Moderate: "#f6ad55",
  High: "#fc8181",
  "Very High": "#c53030",
};

const POLLUTANT_COLORS: Record<string, string> = {
  NO2: "#63b3ed",
  PM10: "#b794f4",
  "PM2.5": "#f687b3",
  O3: "#68d391",
  SO2: "#fbd38d",
  default: "#a0aec0",
};

function getPollutantColor(name: string): string {
  return POLLUTANT_COLORS[name] || POLLUTANT_COLORS.default;
}

function getDaqiColor(summary: string): string {
  for (const [key, color] of Object.entries(DAQI_COLORS)) {
    if (summary.toLowerCase().includes(key.toLowerCase())) {
      return color;
    }
  }
  return "#718096";
}

function getDaqiDescription(index: number): string {
  if (index <= 3) return "Low - Ideal for outdoor activities";
  if (index <= 6) return "Moderate - Sensitive individuals should reduce exertion";
  if (index <= 9) return "High - Reduce outdoor activity";
  return "Very High - Avoid strenuous outdoor activity";
}

export function AirQualityPanel({
  data,
  loading,
  error,
  onRetry,
}: AirQualityPanelProps): React.ReactElement {
  const chartData = useMemo<PollutantChartData[]>(() => {
    if (!data?.pollutants) return [];
    return data.pollutants.map((p: Pollutant) => ({
      name: p.name,
      value: p.value,
      units: p.units,
      index: p.index ?? null,
    }));
  }, [data]);

  if (loading) {
    return (
      <Card title="Air Quality" className="air-quality-panel">
        <div className="loading-state">
          <div className="spinner" />
          <p>Loading air quality data...</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Air Quality" className="air-quality-panel">
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
      <Card title="Air Quality" className="air-quality-panel">
        <div className="empty-state">
          <p>Enter an area to view air quality data.</p>
        </div>
      </Card>
    );
  }

  const daqiColor = getDaqiColor(data.summary);

  return (
    <Card title="Air Quality" className="air-quality-panel">
      <div className="panel-header">
        <p className="area">{data.area}</p>
        {data.forecast_date && (
          <p className="forecast-date">
            Forecast: {new Date(data.forecast_date).toLocaleDateString("en-GB")}
          </p>
        )}
      </div>

      <div className="daqi-indicator">
        <div className="daqi-circle" style={{ backgroundColor: daqiColor }}>
          <span className="daqi-value">{data.max_daqi}</span>
          <span className="daqi-label">DAQI</span>
        </div>
        <div className="daqi-info">
          <span className="daqi-summary" style={{ color: daqiColor }}>
            {data.summary}
          </span>
          <p className="daqi-description">{getDaqiDescription(data.max_daqi)}</p>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="chart-section">
          <h4>Pollutant Levels</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip
                formatter={(value: number) => [`${value}`, "Value"]}
              />
              <ReferenceLine y={0} stroke="#718096" />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getPollutantColor(entry.name)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="pollutant-list">
        <h4>Pollutant Details</h4>
        <div className="pollutant-grid">
          {data.pollutants.map((pollutant: Pollutant) => (
            <div key={pollutant.name} className="pollutant-item">
              <span
                className="pollutant-name"
                style={{ color: getPollutantColor(pollutant.name) }}
              >
                {pollutant.name}
              </span>
              <span className="pollutant-value">
                {pollutant.value} {pollutant.units}
              </span>
              {pollutant.band && (
                <span className="pollutant-band">{pollutant.band}</span>
              )}
              {pollutant.index !== null && pollutant.index !== undefined && (
                <span className="pollutant-index">Index: {pollutant.index}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

export default AirQualityPanel;
