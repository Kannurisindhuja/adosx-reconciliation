import React, { useState } from 'react';

function DiscrepancyTable({ items = [] }) {
  const [sortAsc, setSortAsc] = useState(true);

  const safeItems = Array.isArray(items) ? items : [];

  const sortedItems = [...safeItems].sort((a, b) => {
    const valA = parseFloat(a.val_a ?? a.val_b ?? 0);
    const valB = parseFloat(b.val_a ?? b.val_b ?? 0);

    return sortAsc ? valA - valB : valB - valA;
  });

  return (
    <div>
      <button onClick={() => setSortAsc(!sortAsc)}>
        Sort by Value ({sortAsc ? 'Ascending' : 'Descending'})
      </button>

      <table
        border="1"
        cellPadding="8"
        style={{
          width: '100%',
          marginTop: '1rem',
          borderCollapse: 'collapse',
        }}
      >
        <thead>
          <tr>
            <th>Reason</th>
            <th>Record Ref</th>
            <th>Location</th>
            <th>Org</th>
            <th>System A Value</th>
            <th>System B Value</th>
          </tr>
        </thead>

        <tbody>
          {sortedItems.length === 0 ? (
            <tr>
              <td colSpan="6" style={{ textAlign: 'center' }}>
                No discrepancies found
              </td>
            </tr>
          ) : (
            sortedItems.map((row, idx) => (
              <tr key={idx}>
                <td>
                  <strong>{row.reason}</strong>
                </td>
                <td>{row.record_id}</td>
                <td>{row.location_id}</td>
                <td>{row.org_id}</td>
                <td>{row.val_a ?? '—'}</td>
                <td>{row.val_b ?? '—'}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default DiscrepancyTable;
