import { useEffect, useMemo, useState } from 'react'

type NavView = 'dashboard' | 'knowledge' | 'new-proposal' | 'history' | 'settings'
type Org = { id: string; name: string; slug: string }
type AuthUserMembership = {
  organization_id: string
  organization_name: string
  organization_slug: string
  role: string
}
type AuthUser = {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  memberships: AuthUserMembership[]
}
type AuthResponse = {
  access_token: string
  token_type: string
  user: AuthUser
}
type Category = { id: string; name: string; slug: string; category_type: string; status: string }
type Section = { id: string; name: string; slug: string; content: string; version: number }
type Tag = { id: string; name: string; tag_type: string }
type PortfolioItem = {
  id: string
  project_code: string
  project_name: string
  technologies: string[]
  outcomes: string | null
  status?: string
}
type ProposalExample = {
  id: string
  outcome: string
  job_title: string
  title: string
  status?: string
}
type Job = {
  id: string
  title: string
  description: string
  screening_questions: string[]
  latest_user_instruction: string | null
  status?: string
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
  { key: 'settings', label: 'Settings & Import' },
]

function App() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'
  const [view, setView] = useState<NavView>('dashboard')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [token, setToken] = useState(localStorage.getItem('proposal_app_token') ?? '')
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null)

  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [registerEmail, setRegisterEmail] = useState('')
  const [registerPassword, setRegisterPassword] = useState('')
  const [registerName, setRegisterName] = useState('')
  const [registerOrgName, setRegisterOrgName] = useState('')
  const [registerOrgSlug, setRegisterOrgSlug] = useState('')

  const [organizations, setOrganizations] = useState<Org[]>([])
  const [orgName, setOrgName] = useState('')
  const [orgSlug, setOrgSlug] = useState('')
  const [selectedOrgId, setSelectedOrgId] = useState('')

  const [categories, setCategories] = useState<Category[]>([])
  const [sections, setSections] = useState<Section[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [portfolioItems, setPortfolioItems] = useState<PortfolioItem[]>([])
  const [proposalExamples, setProposalExamples] = useState<ProposalExample[]>([])
  const [jobs, setJobs] = useState<Job[]>([])
  const [runs, setRuns] = useState<ProposalRun[]>([])

  const [categoryName, setCategoryName] = useState('')
  const [categorySlug, setCategorySlug] = useState('')
  const [categoryType, setCategoryType] = useState('custom')
  const [searchTerm, setSearchTerm] = useState('')

  const [tagName, setTagName] = useState('')
  const [tagType, setTagType] = useState('skill')

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
  const [importPath, setImportPath] = useState('/workspace/data/knowledge')

  const [tagEntityType, setTagEntityType] = useState('portfolio_item')
  const [tagEntityId, setTagEntityId] = useState('')
  const [tagIdList, setTagIdList] = useState('')

  const questionCount = useMemo(
    () =>
      screeningQuestions
        .split('\n')
        .map((q) => q.trim())
        .filter(Boolean).length,
    [screeningQuestions],
  )

  const filteredPortfolio = useMemo(() => {
    if (!searchTerm.trim()) return portfolioItems
    const q = searchTerm.toLowerCase()
    return portfolioItems.filter(
      (item) =>
        item.project_name.toLowerCase().includes(q) ||
        item.project_code.toLowerCase().includes(q) ||
        item.technologies.join(' ').toLowerCase().includes(q),
    )
  }, [portfolioItems, searchTerm])

  const filteredExamples = useMemo(() => {
    if (!searchTerm.trim()) return proposalExamples
    const q = searchTerm.toLowerCase()
    return proposalExamples.filter(
      (item) => item.title.toLowerCase().includes(q) || item.job_title.toLowerCase().includes(q),
    )
  }, [proposalExamples, searchTerm])

  const withWorkspace = (path: string): string =>
    selectedOrgId ? `${path}${path.includes('?') ? '&' : '?'}workspace_id=${selectedOrgId}` : path

  function saveToken(value: string) {
    if (!value) {
      localStorage.removeItem('proposal_app_token')
    } else {
      localStorage.setItem('proposal_app_token', value)
    }
    setToken(value)
  }

  async function readJson<T>(path: string, options?: RequestInit): Promise<T> {
    const headers = new Headers(options?.headers ?? {})
    if (!headers.has('Content-Type') && options?.body) {
      headers.set('Content-Type', 'application/json')
    }
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
    const response = await fetch(`${apiBaseUrl}${path}`, { ...options, headers })
    if (!response.ok) {
      const message = await response.text()
      throw new Error(message || `Request failed: ${response.status}`)
    }
    return (await response.json()) as T
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

  function applyAuthState(user: AuthUser) {
    setCurrentUser(user)
    const orgs = user.memberships.map((membership) => ({
      id: membership.organization_id,
      name: membership.organization_name,
      slug: membership.organization_slug,
    }))
    setOrganizations(orgs)
    if (orgs.length > 0 && !selectedOrgId) {
      setSelectedOrgId(orgs[0].id)
    }
  }

  async function loadCurrentUser() {
    const me = await readJson<AuthUser>('/auth/me')
    applyAuthState(me)
  }

  async function loadWorkspaceData(orgId = selectedOrgId) {
    if (!orgId) return
    const workspacePath = (path: string) =>
      `${path}${path.includes('?') ? '&' : '?'}workspace_id=${orgId}`
    const [cats, secs, tagList, portfolios, examples, jobList, runList] = await Promise.all([
      readJson<Category[]>(workspacePath('/knowledge-categories')),
      readJson<Section[]>(workspacePath('/app-sections')),
      readJson<Tag[]>(workspacePath('/tags')),
      readJson<PortfolioItem[]>(workspacePath('/portfolio-items')),
      readJson<ProposalExample[]>(workspacePath('/proposal-examples')),
      readJson<Job[]>(workspacePath('/jobs')),
      readJson<ProposalRun[]>(workspacePath('/proposal-runs')),
    ])
    setCategories(cats)
    setSections(secs)
    setTags(tagList)
    setPortfolioItems(portfolios)
    setProposalExamples(examples)
    setJobs(jobList)
    setRuns(runList)
  }

  useEffect(() => {
    if (!token) return
    void wrapAction(loadCurrentUser)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  useEffect(() => {
    if (!token || !selectedOrgId) return
    void wrapAction(async () => {
      await loadWorkspaceData()
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedOrgId, token])

  async function register() {
    const response = await readJson<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email: registerEmail,
        password: registerPassword,
        full_name: registerName || null,
        organization_name: registerOrgName || null,
        organization_slug: registerOrgSlug || null,
      }),
    })
    saveToken(response.access_token)
    applyAuthState(response.user)
    setRegisterEmail('')
    setRegisterPassword('')
    setRegisterName('')
    setRegisterOrgName('')
    setRegisterOrgSlug('')
  }

  async function login() {
    const response = await readJson<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: loginEmail,
        password: loginPassword,
      }),
    })
    saveToken(response.access_token)
    applyAuthState(response.user)
    setLoginEmail('')
    setLoginPassword('')
  }

  async function createOrganization() {
    await readJson<Org>('/organizations', {
      method: 'POST',
      body: JSON.stringify({ name: orgName, slug: orgSlug }),
    })
    setOrgName('')
    setOrgSlug('')
    await loadCurrentUser()
  }

  async function seedDefaults() {
    await readJson<Record<string, number>>(withWorkspace('/setup/seed-defaults'), {
      method: 'POST',
    })
    await loadWorkspaceData()
  }

  async function importMarkdown() {
    await readJson<Record<string, unknown>>(withWorkspace('/imports/markdown'), {
      method: 'POST',
      body: JSON.stringify({ directory_path: importPath }),
    })
    await loadWorkspaceData()
  }

  async function createCategory() {
    await readJson<Category>(withWorkspace('/knowledge-categories'), {
      method: 'POST',
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

  async function createTag() {
    await readJson<Tag>(withWorkspace('/tags'), {
      method: 'POST',
      body: JSON.stringify({ name: tagName, tag_type: tagType }),
    })
    setTagName('')
    await loadWorkspaceData()
  }

  async function syncTagLinks() {
    const parsedTagIds = tagIdList
      .split(',')
      .map((value) => value.trim())
      .filter(Boolean)
    await readJson(withWorkspace('/tag-links/sync'), {
      method: 'POST',
      body: JSON.stringify({
        entity_type: tagEntityType,
        entity_id: tagEntityId,
        tag_ids: parsedTagIds,
      }),
    })
    setTagEntityId('')
    setTagIdList('')
  }

  async function createPortfolio() {
    await readJson<PortfolioItem>(withWorkspace('/portfolio-items'), {
      method: 'POST',
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

  async function archivePortfolioItem(itemId: string) {
    await readJson<PortfolioItem>(withWorkspace(`/portfolio-items/${itemId}`), {
      method: 'PATCH',
      body: JSON.stringify({ status: 'archived' }),
    })
    await loadWorkspaceData()
  }

  async function archiveProposalExample(itemId: string) {
    await readJson<ProposalExample>(withWorkspace(`/proposal-examples/${itemId}`), {
      method: 'PATCH',
      body: JSON.stringify({ status: 'archived' }),
    })
    await loadWorkspaceData()
  }

  async function createJob() {
    await readJson<Job>(withWorkspace('/jobs'), {
      method: 'POST',
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

  async function archiveJob(jobId: string) {
    await readJson<Job>(withWorkspace(`/jobs/${jobId}`), {
      method: 'PATCH',
      body: JSON.stringify({ status: 'archived' }),
    })
    await loadWorkspaceData()
  }

  async function generateRun(jobId: string) {
    await readJson<{ run: ProposalRun }>(withWorkspace('/proposal-runs/generate'), {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId }),
    })
    await loadWorkspaceData()
  }

  async function createOrUpdateSection() {
    const existing = sections.find((item) => item.slug === sectionSlug)
    if (existing) {
      await readJson<Section>(withWorkspace(`/app-sections/${sectionSlug}`), {
        method: 'PATCH',
        body: JSON.stringify({ content: sectionContent, name: sectionName }),
      })
    } else {
      await readJson<Section>(withWorkspace('/app-sections'), {
        method: 'POST',
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

  if (!token) {
    return (
      <main className="auth-shell">
        <h1>Proposal Writing App</h1>
        {error && <p className="error">Error: {error}</p>}
        <section className="stack auth-grid">
          <form className="intake-form">
            <h2>Login</h2>
            <input
              placeholder="Email"
              type="email"
              value={loginEmail}
              onChange={(event) => setLoginEmail(event.target.value)}
            />
            <input
              placeholder="Password"
              type="password"
              value={loginPassword}
              onChange={(event) => setLoginPassword(event.target.value)}
            />
            <button
              type="button"
              className="primary"
              disabled={!loginEmail || !loginPassword || loading}
              onClick={() => void wrapAction(login)}
            >
              Login
            </button>
          </form>

          <form className="intake-form">
            <h2>Register</h2>
            <input
              placeholder="Email"
              type="email"
              value={registerEmail}
              onChange={(event) => setRegisterEmail(event.target.value)}
            />
            <input
              placeholder="Password"
              type="password"
              value={registerPassword}
              onChange={(event) => setRegisterPassword(event.target.value)}
            />
            <input
              placeholder="Full name (optional)"
              value={registerName}
              onChange={(event) => setRegisterName(event.target.value)}
            />
            <input
              placeholder="Initial workspace name (optional)"
              value={registerOrgName}
              onChange={(event) => setRegisterOrgName(event.target.value)}
            />
            <input
              placeholder="Initial workspace slug (optional)"
              value={registerOrgSlug}
              onChange={(event) => setRegisterOrgSlug(event.target.value)}
            />
            <button
              type="button"
              className="primary"
              disabled={!registerEmail || !registerPassword || loading}
              onClick={() => void wrapAction(register)}
            >
              Register
            </button>
          </form>
        </section>
      </main>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>Proposal Assistant</h1>
        <p className="sidebar-note">API: {apiBaseUrl}</p>
        <p className="sidebar-note">
          Signed in as <strong>{currentUser?.email ?? 'unknown'}</strong>
        </p>
        <button
          type="button"
          className="ghost"
          onClick={() => {
            saveToken('')
            setCurrentUser(null)
            setSelectedOrgId('')
            setOrganizations([])
          }}
        >
          Logout
        </button>
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
            <h2>Project Status</h2>
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
            <input
              placeholder="Search local records"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />

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
            <div className="preview">
              <h3>Categories</h3>
              {categories.map((category) => (
                <div className="item-card" key={category.id}>
                  <strong>{category.name}</strong> ({category.slug}) · {category.category_type} ·{' '}
                  {category.status}
                </div>
              ))}
            </div>

            <form className="intake-form">
              <h3>Create tag</h3>
              <input
                placeholder="Tag name"
                value={tagName}
                onChange={(event) => setTagName(event.target.value)}
              />
              <input
                placeholder="Tag type"
                value={tagType}
                onChange={(event) => setTagType(event.target.value)}
              />
              <button
                type="button"
                className="primary"
                disabled={!selectedOrgId || !tagName || loading}
                onClick={() => void wrapAction(createTag)}
              >
                Create tag
              </button>
            </form>
            <div className="preview">
              <h3>Tags</h3>
              {tags.map((tag) => (
                <div className="item-card" key={tag.id}>
                  {tag.name} <span className="subtle">({tag.tag_type})</span>
                </div>
              ))}
            </div>

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
            <div className="preview">
              <h3>Portfolio records</h3>
              {filteredPortfolio.map((item) => (
                <div className="item-card" key={item.id}>
                  <strong>
                    {item.project_name} ({item.project_code})
                  </strong>
                  <p>{item.technologies.join(', ')}</p>
                  <p>{item.outcomes ?? 'No outcomes yet.'}</p>
                  <button
                    type="button"
                    className="ghost"
                    disabled={loading}
                    onClick={() => void wrapAction(async () => archivePortfolioItem(item.id))}
                  >
                    Archive
                  </button>
                </div>
              ))}
            </div>

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
            <div className="preview">
              <h3>Proposal examples</h3>
              {filteredExamples.map((item) => (
                <div className="item-card" key={item.id}>
                  <strong>{item.title}</strong>
                  <p>{item.job_title}</p>
                  <p>Outcome: {item.outcome}</p>
                  <button
                    type="button"
                    className="ghost"
                    disabled={loading}
                    onClick={() => void wrapAction(async () => archiveProposalExample(item.id))}
                  >
                    Archive
                  </button>
                </div>
              ))}
            </div>
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
                    <button
                      type="button"
                      className="ghost"
                      disabled={loading}
                      onClick={() => void wrapAction(async () => archiveJob(job.id))}
                    >
                      Archive
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
                          {run.screening_answers.map((qa, index) => (
                            <li key={`${run.id}-${index}`}>
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
            <h2>Application Sections & Import</h2>
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

            <form className="intake-form">
              <h3>Import Markdown Knowledge</h3>
              <input
                placeholder="Directory path"
                value={importPath}
                onChange={(event) => setImportPath(event.target.value)}
              />
              <button
                type="button"
                className="primary"
                disabled={!selectedOrgId || !importPath || loading}
                onClick={() => void wrapAction(importMarkdown)}
              >
                Import directory
              </button>
            </form>

            <form className="intake-form">
              <h3>Sync Tag Links</h3>
              <input
                placeholder="Entity type (portfolio_item, proposal_example, job, app_section)"
                value={tagEntityType}
                onChange={(event) => setTagEntityType(event.target.value)}
              />
              <input
                placeholder="Entity ID"
                value={tagEntityId}
                onChange={(event) => setTagEntityId(event.target.value)}
              />
              <input
                placeholder="Tag IDs comma separated"
                value={tagIdList}
                onChange={(event) => setTagIdList(event.target.value)}
              />
              <button
                type="button"
                className="primary"
                disabled={!selectedOrgId || !tagEntityId || loading}
                onClick={() => void wrapAction(syncTagLinks)}
              >
                Sync tags
              </button>
            </form>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
