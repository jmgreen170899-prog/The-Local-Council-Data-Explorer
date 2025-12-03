/**
 * Layout component.
 *
 * A wrapper component that provides consistent page layout.
 */

import React from "react";

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps): React.ReactElement {
  return (
    <div className="layout">
      <header className="layout-header">
        <h1>Local Council Data Explorer</h1>
      </header>
      <main className="layout-main">{children}</main>
      <footer className="layout-footer">
        <p>&copy; {new Date().getFullYear()} Local Council Data Explorer</p>
      </footer>
    </div>
  );
}

export default Layout;
