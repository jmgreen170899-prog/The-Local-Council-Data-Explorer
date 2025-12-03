/**
 * AirQualityPanel component.
 *
 * Displays air quality information for a given area.
 */

import React from "react";
import type { AirQualityResponse } from "./types";

interface AirQualityPanelProps {
  data?: AirQualityResponse;
}

export function AirQualityPanel({ data }: AirQualityPanelProps): React.ReactElement {
  if (!data) {
    return <div>Loading air quality data...</div>;
  }

  return (
    <div className="air-quality-panel">
      <h2>Air Quality</h2>
      <p>Area: {data.area}</p>
      <p>
        DAQI: {data.max_daqi} ({data.summary})
      </p>
      <h3>Pollutants</h3>
      <ul>
        {data.pollutants.map((pollutant) => (
          <li key={pollutant.name}>
            {pollutant.name}: {pollutant.value} {pollutant.units}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AirQualityPanel;
