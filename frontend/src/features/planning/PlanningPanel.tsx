/**
 * PlanningPanel component.
 *
 * Displays planning application information for a local planning authority.
 */

import React from "react";
import type { PlanningResponse } from "./types";

interface PlanningPanelProps {
  data?: PlanningResponse;
}

export function PlanningPanel({ data }: PlanningPanelProps): React.ReactElement {
  if (!data) {
    return <div>Loading planning applications...</div>;
  }

  return (
    <div className="planning-panel">
      <h2>Planning Applications</h2>
      <p>Local Planning Authority: {data.lpa}</p>
      <ul>
        {data.applications.map((app, index) => (
          <li key={index}>
            <strong>{app.reference}</strong>: {app.proposal}
            <br />
            Address: {app.address}
            <br />
            Status: {app.status} | Received: {app.received_date}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default PlanningPanel;
