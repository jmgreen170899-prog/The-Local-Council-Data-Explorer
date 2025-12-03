/**
 * App component.
 *
 * Main application component integrating all feature panels with navigation.
 */

import { useState, useCallback, useMemo } from "react";
import "./App.css";
import Layout, { type TabId } from "./components/Layout";
import BinPanel from "./features/bins/BinPanel";
import PlanningPanel from "./features/planning/PlanningPanel";
import AirQualityPanel from "./features/air/AirQualityPanel";
import { fetchBinCollections } from "./features/bins/api";
import { fetchPlanningApplications } from "./features/planning/api";
import { fetchAirQuality } from "./features/air/api";
import { useApi } from "./hooks/useApi";
import type { BinCollectionResponse } from "./features/bins/types";
import type { PlanningResponse } from "./features/planning/types";
import type { AirQualityResponse } from "./features/air/types";

const DEFAULT_POSTCODE = "YO1 1AA";
const DEFAULT_LPA = "City of York Council";
const DEFAULT_AREA = "Yorkshire & Humber";

function App() {
  const [activeTab, setActiveTab] = useState<TabId>("bins");

  const binFetcher = useCallback(
    () => fetchBinCollections(DEFAULT_POSTCODE),
    []
  );
  const planningFetcher = useCallback(
    () => fetchPlanningApplications(DEFAULT_LPA),
    []
  );
  const airFetcher = useCallback(() => fetchAirQuality(DEFAULT_AREA), []);

  const binsApi = useApi<BinCollectionResponse>(binFetcher, [], true);
  const planningApi = useApi<PlanningResponse>(planningFetcher, [], true);
  const airApi = useApi<AirQualityResponse>(airFetcher, [], true);

  const activePanel = useMemo(() => {
    switch (activeTab) {
      case "bins":
        return (
          <BinPanel
            data={binsApi.data}
            loading={binsApi.loading}
            error={binsApi.error}
            onRetry={binsApi.refetch}
          />
        );
      case "planning":
        return (
          <PlanningPanel
            data={planningApi.data}
            loading={planningApi.loading}
            error={planningApi.error}
            onRetry={planningApi.refetch}
          />
        );
      case "air":
        return (
          <AirQualityPanel
            data={airApi.data}
            loading={airApi.loading}
            error={airApi.error}
            onRetry={airApi.refetch}
          />
        );
      default:
        return null;
    }
  }, [activeTab, binsApi, planningApi, airApi]);

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      <div className="dashboard">
        {activePanel}
      </div>
    </Layout>
  );
}

export default App;
