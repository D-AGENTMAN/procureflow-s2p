"use client";

import { FormEvent, useEffect, useState } from "react";

type Project = {
  id: number;
  project_code: string;
  name: string;
  category: string;
  owner: string;
  estimated_budget: number;
  currency: string;
  status: string;
  description: string;
};

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  async function loadProjects() {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API}/api/sourcing-projects`, { cache: "no-store" });
      if (!response.ok) throw new Error("Could not load sourcing projects.");
      setProjects(await response.json());
    } catch {
      setError("Cannot connect to the API. Make sure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadProjects(); }, []);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    setSaving(true);
    setError("");
    const form = new FormData(formElement);
    const payload = {
      name: String(form.get("name")),
      category: String(form.get("category")),
      owner: String(form.get("owner")),
      estimated_budget: Number(form.get("estimated_budget")),
      currency: "INR",
      description: String(form.get("description") ?? ""),
    };
    try {
      const response = await fetch(`${API}/api/sourcing-projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail?.[0]?.msg ?? body.detail ?? "Could not create project.");
      }
      setShowForm(false);
      formElement.reset();
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setSaving(false);
    }
  }

  const totalBudget = projects.reduce((sum, p) => sum + p.estimated_budget, 0);

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">P</span><span>ProcureFlow</span></div>
        <div className="nav-label">WORKSPACE</div>
        <a className="nav-item active">▦ &nbsp; Overview</a>
        <a className="nav-item">◇ &nbsp; Sourcing projects</a>
        <a className="nav-item disabled">♧ &nbsp; Suppliers <small>Later</small></a>
        <a className="nav-item disabled">▤ &nbsp; Contracts <small>Later</small></a>
        <a className="nav-item disabled">▣ &nbsp; Purchase orders <small>Later</small></a>
        <div className="sidebar-bottom"><div className="avatar">PF</div><div><b>Demo User</b><small>Procurement team</small></div></div>
      </aside>

      <section className="main">
        <header className="topbar"><span>Procurement workspace / Strategic sourcing</span><span className="user-pill">Demo environment</span></header>
        <div className="content">
          <div className="page-heading">
            <div><p className="eyebrow">PROCUREMENT OVERVIEW</p><h1>Strategic sourcing</h1><p className="subheading">Manage sourcing projects, supplier engagement and commercial evaluations.</p></div>
            <button className="primary-button" onClick={() => setShowForm(!showForm)}>＋ New project</button>
          </div>

          {error && <div className="error">{error}</div>}

          <div className="metrics">
            <div className="metric-card"><span>Active projects</span><strong>{projects.length}</strong><small>All recorded projects</small></div>
            <div className="metric-card"><span>Draft projects</span><strong>{projects.filter(p => p.status === "Draft").length}</strong><small>Awaiting next steps</small></div>
            <div className="metric-card"><span>Estimated project value</span><strong>{totalBudget.toLocaleString("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 })}</strong><small>Sum of project budgets</small></div>
          </div>

          {showForm && <form className="form-card" onSubmit={handleCreate}>
            <div className="form-heading"><div><h2>Create sourcing project</h2><p>Start by capturing the basic project information.</p></div><button type="button" className="close-button" onClick={() => setShowForm(false)}>×</button></div>
            <div className="form-grid">
              <label>Project name<input name="name" placeholder="e.g. Men's basic T-shirt sourcing" required minLength={3}/></label>
              <label>Category<input name="category" placeholder="e.g. Apparel" required/></label>
              <label>Project owner<input name="owner" placeholder="e.g. Category Manager" required/></label>
              <label>Estimated budget (INR)<input name="estimated_budget" type="number" min="0" step="0.01" placeholder="e.g. 2500000" required/></label>
              <label className="full">Description<textarea name="description" placeholder="Add scope, specifications or business context..."/></label>
            </div>
            <div className="form-actions"><button type="button" className="secondary-button" onClick={() => setShowForm(false)}>Cancel</button><button className="primary-button" disabled={saving}>{saving ? "Saving..." : "Create project"}</button></div>
          </form>}

          <div className="section-heading"><div><h2>Sourcing projects</h2><p>Your procurement initiatives in one place.</p></div><button className="text-button" onClick={loadProjects}>↻ Refresh</button></div>
          <div className="table-card">
            <div className="table-wrap"><table><thead><tr><th>PROJECT</th><th>CATEGORY</th><th>OWNER</th><th>ESTIMATED BUDGET</th><th>STATUS</th></tr></thead>
              <tbody>
                {loading ? <tr><td colSpan={5} className="empty">Loading projects...</td></tr> :
                  projects.length === 0 ? <tr><td colSpan={5} className="empty">No projects yet. Create your first sourcing project to get started.</td></tr> :
                  projects.map(p => <tr key={p.id}><td><b>{p.name}</b><small>{p.project_code}</small></td><td>{p.category}</td><td>{p.owner}</td><td>{p.estimated_budget.toLocaleString("en-IN", { style: "currency", currency: p.currency, maximumFractionDigits: 0 })}</td><td><span className="status">{p.status}</span></td></tr>)}
              </tbody>
            </table></div>
          </div>
          <p className="footnote">ProcureFlow v0.1 · Portfolio learning project · Demo data only</p>
        </div>
      </section>
    </main>
  );
}
