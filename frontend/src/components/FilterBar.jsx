function FilterBar({
  orgId,
  setOrgId,
  reason,
  setReason,
}) {
  return (
    <div className="filter-bar">
      <div>
        <label>Organization</label>

        <select
          value={orgId}
          onChange={(e) => setOrgId(e.target.value)}
        >
          <option value="ORG-A">ORG-A</option>
          <option value="ORG-B">ORG-B</option>
        </select>
      </div>

      <div>
        <label>Reason</label>

        <select
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        >
          <option value="ALL">All</option>

          <option value="Missing in System B">
            Missing in System B
          </option>

          <option value="Orphan record in System B">
            Orphan in System B
          </option>

          <option value="Duplicate entry in System B">
            Duplicate in System B
          </option>

          <option value="Value mismatch">
            Value mismatch
          </option>
        </select>
      </div>
    </div>
  );
}

export default FilterBar;