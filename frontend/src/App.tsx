import { useMemo, useState } from 'react'

type NavView =
  | 'dashboard'
  | 'knowledge'
  | 'new-proposal'
  | 'history'
  | 'settings'

const navItems: Array<{ key: NavView; label: string }> = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'knowledge', label: 'Knowledge Base' },
  { key: 'new-proposal', label: 'New Proposal' },
  { key: 'history', label: 'Proposal History' },
  { key: 'settings', label: 'App Sections' },
]

function App() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'
  const [view, setView] = useState<NavView>('dashboard')
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [screeningQuestions, setScreeningQuestions] = useState('')
  const [userInstruction, setUserInstruction] = useState('')

  const questionCount = useMemo(
    () =>
      screeningQuestions
        .split('\n')
        .map((q) => q.trim())
        .filter(Boolean).length,
    [screeningQuestions],
  )

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>Proposal Assistant</h1>
        <p className="sidebar-note">MVP foundation aligned to PRD v1.0</p>
        <nav>
          {navItems.map((item) => (
            <button
              key={item.key}
              className={view === item.key ? 'active' : ''}
              onClick={() => setView(item.key)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="content">
        {view === 'dashboard' && (
          <section>
            <h2>Foundation Status</h2>
            <div className="grid">
              <article>
                <h3>Backend</h3>
                <p>FastAPI API + SQLAlchemy + Alembic migration baseline.</p>
              </article>
              <article>
                <h3>Frontend</h3>
                <p>React + TypeScript admin shell with proposal intake scaffold.</p>
              </article>
              <article>
                <h3>Data Layer</h3>
                <p>Tenant-aware organizations, users, and memberships initialized.</p>
              </article>
              <article>
                <h3>Next</h3>
                <p>Knowledge entities, retrieval services, and proposal run orchestration.</p>
              </article>
            </div>
            <p className="subtle">Configured API base URL: {apiBaseUrl}</p>
          </section>
        )}

        {view === 'knowledge' && (
          <section>
            <h2>Knowledge Modules (MVP plan)</h2>
            <ul className="checklist">
              <li>Portfolio Items</li>
              <li>Winning Proposals + Screening Q&A</li>
              <li>About Me Section</li>
              <li>Proposal Instructions Section</li>
              <li>Custom Section Definitions</li>
            </ul>
          </section>
        )}

        {view === 'new-proposal' && (
          <section>
            <h2>New Proposal Intake</h2>
            <p className="subtle">
              This form mirrors the PRD input contract for job-based proposal generation.
            </p>
            <form className="intake-form">
              <label>
                Job Title
                <input
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="Senior FastAPI developer for proposal system"
                />
              </label>
              <label>
                Job Description
                <textarea
                  rows={7}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste client description and requirements..."
                />
              </label>
              <label>
                Screening Questions (one per line)
                <textarea
                  rows={5}
                  value={screeningQuestions}
                  onChange={(e) => setScreeningQuestions(e.target.value)}
                />
              </label>
              <label>
                Latest User Instruction (optional)
                <textarea
                  rows={3}
                  value={userInstruction}
                  onChange={(e) => setUserInstruction(e.target.value)}
                />
              </label>
              <button type="button" className="primary">
                Generate (API integration next)
              </button>
            </form>

            <div className="preview">
              <h3>Draft Metadata Preview</h3>
              <p>
                <strong>Title:</strong> {jobTitle || '—'}
              </p>
              <p>
                <strong>Description chars:</strong> {jobDescription.length}
              </p>
              <p>
                <strong>Screening questions:</strong> {questionCount}
              </p>
              <p>
                <strong>User instruction provided:</strong> {userInstruction ? 'Yes' : 'No'}
              </p>
            </div>
          </section>
        )}

        {view === 'history' && (
          <section>
            <h2>Proposal History</h2>
            <p>Placeholder for persisted proposal runs, selected evidence, and outputs.</p>
          </section>
        )}

        {view === 'settings' && (
          <section>
            <h2>Application Sections</h2>
            <p>
              About Me and Proposal Instructions will be managed as configurable sections in
              the backend.
            </p>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
