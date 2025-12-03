/**
 * ChartWrapper component.
 *
 * A wrapper component for rendering charts with consistent styling.
 */

import React from "react";

interface ChartWrapperProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function ChartWrapper({
  title,
  children,
  className = "",
}: ChartWrapperProps): React.ReactElement {
  return (
    <div className={`chart-wrapper ${className}`}>
      {title && <h4 className="chart-title">{title}</h4>}
      <div className="chart-container">{children}</div>
    </div>
  );
}

export default ChartWrapper;
