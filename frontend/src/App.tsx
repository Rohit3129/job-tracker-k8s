import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Application {
  id: number
  company: string
  role: string
  status: string
  applied_date: string
}

function App() {
  const [applications, setApplications] = useState<Application[]>([])
  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [status, setStatus] = useState('applied')
  const [error, setError] = useState('')

  const fetchApplications = async () => {
    try {
      const res = await fetch(`${API_URL}/applications`)
      if (!res.ok) throw new Error('Failed to fetch')
      const data = await res.json()
      setApplications(data)
      setError('')
    } catch (e) {
      setError('Could not reach backend API')
    }
  }

  useEffect(() => {
    fetchApplications()
  }, [])

  const addApplication = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!company || !role) return
    try {
      await fetch(`${API_URL}/applications`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company, role, status }),
      })
      setCompany('')
      setRole('')
      setStatus('applied')
      fetchApplications()
    } catch {
      setError('Could not add application')
    }
  }

  const deleteApplication = async (id: number) => {
    await fetch(`${API_URL}/applications/${id}`, { method: 'DELETE' })
    fetchApplications()
  }

  return (
    <div style={{ maxWidth: 700, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>Job Application Tracker v2</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <form onSubmit={addApplication} style={{ marginBottom: 24, display: 'flex', gap: 8 }}>
        <input placeholder="Company" value={company} onChange={(e) => setCompany(e.target.value)} />
        <input placeholder="Role" value={role} onChange={(e) => setRole(e.target.value)} />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="applied">Applied</option>
          <option value="interview">Interview</option>
          <option value="offer">Offer</option>
          <option value="rejected">Rejected</option>
        </select>
        <button type="submit">Add</button>
      </form>

      <table width="100%" cellPadding={8} style={{ borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ textAlign: 'left', borderBottom: '2px solid #ccc' }}>
            <th>Company</th>
            <th>Role</th>
            <th>Status</th>
            <th>Applied</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {applications.map((app) => (
            <tr key={app.id} style={{ borderBottom: '1px solid #eee' }}>
              <td>{app.company}</td>
              <td>{app.role}</td>
              <td>{app.status}</td>
              <td>{app.applied_date}</td>
              <td>
                <button onClick={() => deleteApplication(app.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default App
