import { useState } from 'react'
import { Pencil, Check, X, User, Star } from 'lucide-react'
import './profile-view.css'

export function ProfileView({ userName, email, acquiredSkills, onUpdateName, addToast }) {
  const [editing, setEditing] = useState(false)
  const [draftName, setDraftName] = useState(userName)

  const totalPoints = acquiredSkills.reduce((acc, s) => acc + s.points, 0)

  const handleSave = () => {
    if (!draftName.trim()) {
      addToast('error', 'Name cannot be empty.')
      return
    }
    onUpdateName(draftName.trim())
    setEditing(false)
    addToast('success', 'Profile updated successfully.')
  }

  const handleCancel = () => {
    setDraftName(userName)
    setEditing(false)
  }

  return (
    <main className="profile-main">
      {/* Profile Card */}
      <section className="profile-card">
        <div className="profile-card-content">
          {/* Avatar */}
          <div className="profile-avatar">
            <User className="w-9 h-9" style={{ color: '#6B3A4F' }} />
          </div>

          {/* Info */}
          <div className="profile-info-section">
            <div className="profile-name-row">
              {editing ? (
                <input
                  type="text"
                  value={draftName}
                  onChange={(e) => setDraftName(e.target.value)}
                  autoFocus
                  className="profile-name-input"
                  aria-label="Edit name"
                />
              ) : (
                <h2 className="profile-name-display">{userName}</h2>
              )}
              {editing ? (
                <div className="profile-name-actions">
                  <button onClick={handleSave} className="profile-name-save" aria-label="Save name">
                    <Check className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={handleCancel} className="profile-name-cancel" aria-label="Cancel editing">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <button onClick={() => setEditing(true)} className="profile-name-button" aria-label="Edit name">
                  <Pencil className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
            <p className="profile-email">{email}</p>
          </div>

          {/* Stats */}
          <div className="profile-stats">
            <div className="profile-stat">
              <p className="profile-stat-value">{acquiredSkills.length}</p>
              <p className="profile-stat-label">Skills</p>
            </div>
            <div className="profile-stat">
              <p className="profile-stat-value">{totalPoints}</p>
              <p className="profile-stat-label">Total Points</p>
            </div>
          </div>
        </div>
      </section>

      {/* Acquired Skills Table */}
      <section className="profile-skills-section">
        <div className="profile-skills-header">
          <Star className="w-4 h-4 text-primary" style={{ color: '#c2607a' }} />
          <h3 className="profile-skills-title">Acquired Skills</h3>
          <span className="profile-skills-count">{acquiredSkills.length} skill{acquiredSkills.length !== 1 ? 's' : ''}</span>
        </div>

        {acquiredSkills.length === 0 ? (
          <div className="profile-empty-state">
            <div className="profile-empty-icon">
              <Star className="w-6 h-6 text-muted-foreground" />
            </div>
            <p className="profile-empty-text">You haven&apos;t acquired any skills yet.</p>
            <p className="profile-empty-text">Visit the Skills Catalog to place your first order.</p>
          </div>
        ) : (
          <div className="profile-table-wrapper">
            <table className="profile-table">
              <thead className="profile-table-head">
                <tr>
                  <th className="profile-table-header">Skill</th>
                  <th className="profile-table-header">Points Accumulated</th>
                </tr>
              </thead>
              <tbody>
                {acquiredSkills.map((skill, idx) => (
                  <tr key={skill.name} className={`profile-table-row ${idx % 2 === 0 ? '' : 'profile-table-row-alt'}`}>
                    <td className="profile-table-cell profile-table-cell-skill">{skill.name}</td>
                    <td className="profile-table-cell profile-table-cell-points">
                      <span className="profile-points-badge">
                        {skill.points} pt{skill.points !== 1 ? 's' : ''}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  )
}
