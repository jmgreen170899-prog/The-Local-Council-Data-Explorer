/**
 * BinPanel component.
 *
 * Displays bin collection information for a given address.
 */

import React from "react";
import type { BinCollectionResponse } from "./types";

interface BinPanelProps {
  data?: BinCollectionResponse;
}

export function BinPanel({ data }: BinPanelProps): React.ReactElement {
  if (!data) {
    return <div>Loading bin collection data...</div>;
  }

  return (
    <div className="bin-panel">
      <h2>Bin Collections</h2>
      <p>Address: {data.address}</p>
      <p>Council: {data.council}</p>
      <ul>
        {data.bins.map((bin) => (
          <li key={`${bin.type}-${bin.collection_date}`}>
            {bin.type}: {bin.collection_date}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default BinPanel;
