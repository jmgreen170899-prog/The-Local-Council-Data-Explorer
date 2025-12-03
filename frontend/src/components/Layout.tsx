/**
 * Layout component.
 *
 * A wrapper component that provides consistent page layout with navigation.
 */

import React from "react";

type TabId = "bins" | "planning" | "air";

interface LayoutProps {
  children: React.ReactNode;
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

interface TabConfig {
  id: TabId;
  label: string;
  icon: string;
}

const TABS: TabConfig[] = [
  { id: "bins", label: "Bin Collections", icon: "🗑️" },
  { id: "planning", label: "Planning", icon: "🏗️" },
  { id: "air", label: "Air Quality", icon: "🌬️" },
];

export function Layout({
  children,
  activeTab,
  onTabChange,
}: LayoutProps): React.ReactElement {
  return (
    <div className="layout">
      <header className="layout-header">
        <h1>Local Council Data Explorer</h1>
        <nav className="layout-nav">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`nav-tab ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => onTabChange(tab.id)}
              aria-current={activeTab === tab.id ? "page" : undefined}
            >
              <span className="nav-icon">{tab.icon}</span>
              <span className="nav-label">{tab.label}</span>
            </button>
          ))}
        </nav>
      </header>
      <main className="layout-main">{children}</main>
      <footer className="layout-footer">
        <p>&copy; {new Date().getFullYear()} Local Council Data Explorer</p>
      </footer>
    </div>
  );
}

export type { TabId };
export default Layout;
