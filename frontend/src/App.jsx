import { useEffect, useState } from "react";
import axios from "axios";
import FilterBar from "./components/FilterBar";
import DiscrepancyTable from "./components/DiscrepancyTable";
import "./index.css";

const API_URL = `${import.meta.env.VITE_API_URL}/api/discrepancies/`;

function App() {
  const [orgId, setOrgId] = useState("ORG-A");
  const [reason, setReason] = useState("ALL");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchDiscrepancies = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await axios.get(API_URL, {
        params: {
          org_id: orgId,
          reason: reason,
        },
      });

      setData(response.data.results || []);
    } catch (err) {
      console.error(err);
      setError("Unable to connect to the backend.");
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDiscrepancies();
  }, [orgId, reason]);

  return (
    <div className="container">
      <h1>Cross-System Reconciliation</h1>

      <p className="subtitle">
        Review disagreements between System A and System B
      </p>

      <FilterBar
        orgId={orgId}
        setOrgId={setOrgId}
        reason={reason}
        setReason={setReason}
      />

      {loading && <p>Loading...</p>}

      {error && <p className="error">{error}</p>}

      {!loading && !error && (
        <>
          <div className="summary">
            Discrepancies found: <strong>{data.length}</strong>
          </div>

          <DiscrepancyTable items={data} />
        </>
      )}
    </div>
  );
}

export default App;
