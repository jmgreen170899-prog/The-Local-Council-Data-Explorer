/**
 * Card component.
 *
 * A reusable card container for displaying content with consistent styling.
 */

import React from "react";

interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
}

export function Card({
  title,
  children,
  className = "",
  actions,
}: CardProps): React.ReactElement {
  return (
    <div className={`card ${className}`}>
      {(title || actions) && (
        <div className="card-header">
          {title && <h3 className="card-title">{title}</h3>}
          {actions && <div className="card-actions">{actions}</div>}
        </div>
      )}
      <div className="card-content">{children}</div>
    </div>
  );
}

export default Card;
