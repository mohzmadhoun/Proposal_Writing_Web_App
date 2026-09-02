import { useEffect, useMemo, useState } from 'react'

type NavView = 'dashboard' | 'knowledge' | 'new-proposal' | 'history' | 'settings'
type Org = { id: string; name: string; slug: string }
type Category = { id: string; name: string; slug: string; category_type: string; status: string }
type Section = { id: string; name: string; slug: string; content: string; version: number }
type PortfolioItem = {
  id: string
  project_code: string
  project_name: string
  technologies: string[]
  outcomes: string | null
}
type ProposalExample = { id: string; outcome: string; job_title: string; title: string }
type Job = {
  id: string
  title: string
  description: string
  screening_questions: string[]
  latest_user_instruction: string | null
}
type ProposalRun = {
  id: string
  job_id: string
  proposal_text: string
  screening_answers: Array<{ question: string; answer: string }>
  created_at: string
}

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
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const [organizations, setOrganizations] = useState<Org[]>([])
  const [orgName, setOrgName] = useState('')
  const [orgSlug, setOrgSlug] = useState('')
  const [selectedOrgId, setSelectedOrgId] = useState('')

  const [categories, setCategories] = useState<Category[]>([])
  const [sections, setSections] = useState<Section[]>([])
  const [portfolioItems, setPortfolioItems] = useState<PortfolioItem[]>([])
  const [proposalExamples, setProposalExamples] = useState<ProposalExample[]>([])
  const [jobs, setJobs] = useState<Job[]>([])
  const [runs, setRuns] = useState<ProposalRun[]>([])

  const [categoryName, setCategoryName] = useState('')
  const [categorySlug, setCategorySlug] = useState('')
  const [categoryType, setCategoryType] = useState('custom')

  const [portfolioTitle, setPortfolioTitle] = useState('')
  const [portfolioCode, setPortfolioCode] = useState('')
  const [portfolioName, setPortfolioName] = useState('')
  const [portfolioTech, setPortfolioTech] = useState('')
  const [portfolioOutcome, setPortfolioOutcome] = useState('')

  const [exampleTitle, setExampleTitle] = useState('')
  const [exampleJobTitle, setExampleJobTitle] = useState('')
  const [exampleJobDescription, setExampleJobDescription] = useState('')
  const [exampleProposal, setExampleProposal] = useState('')
  const [exampleOutcome, setExampleOutcome] = useState('hired')

  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [screeningQuestions, setScreeningQuestions] = useState('')
  const [userInstruction, setUserInstruction] = useState('')

  const [sectionName, setSectionName] = useState('About Me')
  const [sectionSlug, setSectionSlug] = useState('about-me')
  const [sectionContent, setSectionContent] = useState('')

  const questionCount = useMemo(
    () =>
      screeningQuestions
        .split('\n')
        .map((q) => q.trim())
        .filter(Boolean).length,
    [screeningQuestions],
  )

  const withWorkspace = (path: string): string =>
    selectedOrgId ? `${path}${path.includes('?') ? '&' : '?'}workspace_id=${selectedOrgId}` : path

  async function readJson<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${apiBaseUrl}${path}`, options)
    if (!response.ok) {
      const message = await response.text()
      throw new Error(message || `Request failed: ${response.status}`)
    }
    return (await response.json()) as T
  }

  async function loadOrganizations() {
    const data = await readJson<Org[]>('/organizations')
    setOrganizations(data)
    if (!selectedOrgId && data.length > 0) {
      setSelectedOrgId(data[0].id)
    }
  }

  async function loadWorkspaceData(orgId = selectedOrgId) {
    if (!orgId) return
    const workspacePath = (path: string) =>
      `${path}${path.includes('?') ? '&' : '?'}workspace_id=${orgId}`
    const [cats, secs, portfolios, examples, jobList, runList] = await Promise.all([
      readJson<Category[]>(workspacePath('/knowledge-categories')),
      readJson<Section[]>(workspacePath('/app-sections')),
      readJson<PortfolioItem[]>(workspacePath('/portfolio-items')),
      readJson<ProposalExample[]>(workspacePath('/proposal-examples')),
      readJson<Job[]>(workspacePath('/jobs')),
      readJson<ProposalRun[]>(workspacePath('/proposal-runs')),
    ])
    setCategories(cats)
    setSections(secs)
    setPortfolioItems(portfolios)
    setProposalExamples(examples)
    setJobs(jobList)
    setRuns(runList)
  }

  async function wrapAction(action: () => Promise<void>) {
    setError(null)
    setLoading(true)
    try {
      await action()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unexpected error'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void wrapAction(loadOrganizations)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    void wrapAction(async () => {
      await loadWorkspaceData()
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedOrgId])

  async function createOrganization() {
    await readJson<Org>('/organizations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: orgName, slug: orgSlug }),
    })
    setOrgName('')
    setOrgSlug('')
    await loadOrganizations()
  }

  async function seedDefaults() {
    await readJson<Record<string, number>>(withWorkspace('/setup/seed-defaults'), {
      method: 'POST',
    })
    await loadWorkspaceData()
  }

  async function createCategory() {
    await readJson<Category>(withWorkspace('/knowledge-categories'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: categoryName,
        slug: categorySlug,
        category_type: categoryType,
      }),
    })
    setCategoryName('')
    setCategorySlug('')
    await loadWorkspaceData()
  }

  async function createPortfolio() {
    await readJson<PortfolioItem>(withWorkspace('/portfolio-items'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: portfolioTitle,
        summary: portfolioOutcome,
        content: portfolioOutcome || 'Portfolio evidence record',
        project_code: portfolioCode,
        project_name: portfolioName,
        technologies: portfolioTech
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean),
        outcomes: portfolioOutcome,
      }),
    })
    setPortfolioTitle('')
    setPortfolioCode('')
    setPortfolioName('')
    setPortfolioTech('')
    setPortfolioOutcome('')
    await loadWorkspaceData()
  }

  async function createProposalExample() {
    await readJson<ProposalExample>(withWorkspace('/proposal-examples'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: exampleTitle,
        content: exampleProposal,
        job_title: exampleJobTitle,
        job_description: exampleJobDescription,
        submitted_proposal: exampleProposal,
        outcome: exampleOutcome,
      }),
    })
    setExampleTitle('')
    setExampleJobTitle('')
    setExampleJobDescription('')
    setExampleProposal('')
    await loadWorkspaceData()
  }

  async function createJob() {
    await readJson<Job>(withWorkspace('/jobs'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: jobTitle,
        description: jobDescription,
        latest_user_instruction: userInstruction || null,
        screening_questions: screeningQuestions
          .split('\n')
          .map((item) => item.trim())
          .filter(Boolean),
      }),
    })
    setJobTitle('')
    setJobDescription('')
    setUserInstruction('')
    setScreeningQuestions('')
    await loadWorkspaceData()
  }

  async function generateRun(jobId: string) {
    await readJson<{ run: ProposalRun }>(withWorkspace('/proposal-runs/generate'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId }),
    })
    await loadWorkspaceData()
  }

  async function createOrUpdateSection() {
    const existing = sections.find((item) => item.slug === sectionSlug)
    if (existing) {
      await readJson<Section>(withWorkspace(`/app-sections/${sectionSlug}`), {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: sectionContent, name: sectionName }),
      })
    } else {
      await readJson<Section>(withWorkspace('/app-sections'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: sectionName,
          slug: sectionSlug,
          content: sectionContent,
        }),
      })
    }
    setSectionContent('')
    await loadWorkspaceData()
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>Proposal Assistant</h1>
        <p className="sidebar-note">API: {apiBaseUrl}</p>
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
        {error && <p className="error">Error: {error}</p>}
        <section className="panel">
          <h2>Workspace</h2>
          <div className="row">
            <select
              value={selectedOrgId}
              onChange={(event) => setSelectedOrgId(event.target.value)}
            >
              <option value="">Select workspace</option>
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name} ({org.slug})
                </option>
              ))}
            </select>
            <button
              type="button"
              className="primary"
              disabled={!selectedOrgId || loading}
              onClick={() => void wrapAction(seedDefaults)}
            >
              Seed defaults
            </button>
          </div>
          <div className="row">
            <input
              placeholder="Workspace name"
              value={orgName}
              onChange={(event) => setOrgName(event.target.value)}
            />
            <input
              placeholder="workspace-slug"
              value={orgSlug}
              onChange={(event) => setOrgSlug(event.target.value)}
            />
            <button
              type="button"
              className="primary"
              disabled={loading || !orgName || !orgSlug}
              onClick={() => void wrapAction(createOrganization)}
            >
              Create workspace
            </button>
          </div>
        </section>

        {view === 'dashboard' && (
          <section>
            <h2>Foundation Status</h2>
            <div className="grid">
              <article>
                <h3>Categories</h3>
                <p>{categories.length}</p>
              </article>
              <article>
                <h3>Portfolio Items</h3>
                <p>{portfolioItems.length}</p>
              </article>
              <article>
                <h3>Proposal Examples</h3>
                <p>{proposalExamples.length}</p>
              </article>
              <article>
                <h3>Generated Runs</h3>
                <p>{runs.length}</p>
              </article>
            </div>
          </section>
        )}

        {view === 'knowledge' && (
          <section className="stack">
            <h2>Knowledge Base</h2>
            <form className="intake-form">
              <h3>Create category</h3>
              <input
                placeholder="Category name"
                value={categoryName}
                onChange={(event) => setCategoryName(event.target.value)}
              />
              <input
                placeholder="category-slug"
                value={categorySlug}
                onChange={(event) => setCategorySlug(event.target.value)}
              />
              <input
                placeholder="category type"
                value={categoryType}
                onChange={(event) => setCategoryType(event.target.value)}
              />
              <button
                type="button"
                className="primary"
                disabled={!selectedOrgId || !categoryName || !categorySlug || loading}
                onClick={() => void wrapAction(createCategory)}
              >
                Create category
              </button>
            </form>

            <form className="intake-form">
              <h3>Create portfolio item</h3>
              <input
                placeholder="Title"
                value={portfolioTitle}
                onChange={(event) => setPortfolioTitle(event.target.value)}
              />
              <input
                placeholder="Project code (e.g. PRJ-001)"
                value={portfolioCode}
                onChange={(event) => setPortfolioCode(event.target.value)}
              />
              <input
                placeholder="Project name"
                value={portfolioName}
                onChange={(event) => setPortfolioName(event.target.value)}
              />
              <input
                placeholder="Technologies (comma separated)"
                value={portfolioTech}
                onChange={(event) => setPortfolioTech(event.target.value)}
              />
              <textarea
                rows={3}
                placeholder="Outcomes"
                value={portfolioOutcome}
                onChange={(event) => setPortfolioOutcome(event.target.value)}
              />
              <button
                type="button"
                className="primary"
                disabled={!selectedOrgId || !portfolioTitle || !portfolioCode || loading}
                onClick={() => void wrapAction(createPortfolio)}
              >
                Save portfolio item
              </button>
            </form>

            <form className="intake-form">
              <h3>Create proposal example</h3>
              <input
                placeholder="Record title"
                value={exampleTitle}
                onChange={(event) => setExampleTitle(event.target.value)}
              />
              <input
                placeholder="Job title"
                value={exampleJobTitle}
                onChange={(event) => setExampleJobTitle(event.target.value)}
              />
              <textarea
                rows={4}
                placeholder="Job description"
                value={exampleJobDescription}
                onChange={(event) => setExampleJobDescription(event.target.value)}
              />
              <textarea
                rows={4}
                placeholder="Submitted proposal"
                value={exampleProposal}
                onChange={(event) => setExampleProposal(event.target.value)}
              />
              <input
                placeholder="Outcome (hired/interviewed/not-hired)"
                value={exampleOutcome}
                onChange={(event) => setExampleOutcome(event.target.value)}
              />
              <button
                type="button"
                className="primary"
                disabled={!selectedOrgId || !exampleTitle || !exampleJobTitle || loading}
                onClick={() => void wrapAction(createProposalExample)}
              >
                Save proposal example
              </button>
            </form>
          </section>
        )}

        {view === 'new-proposal' && (
          <section className="stack">
            <h2>New Proposal Intake</h2>
            <p className="subtle">
              Questions detected: {questionCount} {userInstruction ? '(with user instruction)' : ''}
            </p>
            <form className="intake-form">
              <label>
                Job Title
                <input
                  value={jobTitle}
                  onChange={(event) => setJobTitle(event.target.value)}
                  placeholder="Senior FastAPI developer for proposal system"
                />
              </label>
              <label>
                Job Description
                <textarea
                  rows={7}
                  value={jobDescription}
                  onChange={(event) => setJobDescription(event.target.value)}
                  placeholder="Paste client description and requirements..."
                />
              </label>
              <label>
                Screening Questions (one per line)
                <textarea
                  rows={5}
                  value={screeningQuestions}
                  onChange={(event) => setScreeningQuestions(event.target.value)}
                />
              </label>
              <label>
                Latest User Instruction (optional)
                <textarea
                  rows={3}
                  value={userInstruction}
                  onChange={(event) => setUserInstruction(event.target.value)}
                />
              </label>
              <button
                type="button"
                className="primary"
                disabled={!selectedOrgId || !jobTitle || !jobDescription || loading}
                onClick={() => void wrapAction(createJob)}
              >
                Create job
              </button>
            </form>

            <div className="preview">
              <h3>Jobs</h3>
              {jobs.length === 0 ? (
                <p className="subtle">No jobs yet.</p>
              ) : (
                jobs.map((job) => (
                  <div key={job.id} className="item-card">
                    <h4>{job.title}</h4>
                    <p>{job.description.slice(0, 180)}</p>
                    <button
                      type="button"
                      className="primary"
                      disabled={loading}
                      onClick={() => void wrapAction(async () => generateRun(job.id))}
                    >
                      Generate proposal run
                    </button>
                  </div>
                ))
              )}
            </div>
          </section>
        )}

        {view === 'history' && (
          <section>
            <h2>Proposal History</h2>
            {runs.length === 0 ? (
              <p className="subtle">No generated runs yet.</p>
            ) : (
              <div className="stack">
                {runs.map((run) => (
                  <article key={run.id} className="preview">
                    <h3>Run {run.id.slice(0, 8)}</h3>
                    <p className="subtle">{new Date(run.created_at).toLocaleString()}</p>
                    <p>{run.proposal_text.slice(0, 420)}...</p>
                    {run.screening_answers.length > 0 && (
                      <>
                        <h4>Screening answers</h4>
                        <ul>
                          {run.screening_answers.map((qa) => (
                            <li key={qa.question}>
                              <strong>{qa.question}</strong>: {qa.answer}
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>
        )}

        {view === 'settings' && (
          <section className="stack">
            <h2>Application Sections</h2>
            <form className="intake-form">
              <input
                placeholder="Section name"
                value={sectionName}
                onChange={(event) => setSectionName(event.target.value)}
              />
              <input
                placeholder="Section slug"
                value={sectionSlug}
                onChange={(event) => setSectionSlug(event.target.value)}
              />
              <textarea
                rows={8}
                placeholder="Section content"
                value={sectionContent}
                onChange={(event) => setSectionContent(event.target.value)}
              />
              <button
                type="button"
                className="primary"
                disabled={!selectedOrgId || !sectionSlug || !sectionName || loading}
                onClick={() => void wrapAction(createOrUpdateSection)}
              >
                Save section
              </button>
            </form>
            <div className="preview">
              <h3>Current sections</h3>
              {sections.map((section) => (
                <div className="item-card" key={section.id}>
                  <strong>{section.name}</strong> ({section.slug}) v{section.version}
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
