import { User, Star } from 'lucide-react'
import './profile-view.css'

/**
 * Componente de vista de perfil de usuario, mostrando información básica y habilidades adquiridas.
 */
export function ProfileView({ user }) {
  const skills = user?.skills || []

  // Renderizar la vista de perfil
  return (
    <main className="profile-main">
      {/* Tajeta de perfil */}
      <section className="profile-card">
        <div className="profile-card-content">

          {/* Info */}
          <div className="profile-info-section">
            <div className="profile-name-row">
              <h2 className="profile-name-display">{user?.name}</h2>
            </div>
            <p className="profile-email">{user?.email}</p>
          </div>

          {/* Cantidad de habilidades */}
          <div className="profile-stats">
            <div className="profile-stat">
              <p className="profile-stat-value">{skills.length}</p>
              <p className="profile-stat-label">Habilidades</p>
            </div>
          </div>

        </div>

      </section>

      {/* Tabla de Habilidades Adquiridas */}
      <section className="profile-skills-section">
        <div className="profile-skills-header">
          <Star className="w-4 h-4 text-primary" style={{ color: '#c2607a' }} />
          <h3 className="profile-skills-title">Habilidades adquiridas</h3>
        </div>

        {skills.length === 0 ? (
          
          // No hay habilidades adquiridas
          <div className="profile-empty-state">
            <p className="profile-empty-text">No has adquirido ninguna habilidad todavía.</p>
            <p className="profile-empty-text">Visita el Catálogo de Habilidades para realizar tu primer pedido.</p>
          </div>
        
      ) : (
          
          // Tabla de habilidades adquiridas
          <div className="profile-table-wrapper">
            <table className="profile-table">
              
              {/* Encabezado de la tabla */}
              <thead className="profile-table-head">
                <tr>
                  <th className="profile-table-header">Habilidad</th>
                  <th className="profile-table-header2">Puntos </th>
                </tr>
              </thead>
              
              {/* Cuerpo de la tabla con habilidades adquiridas */}
              <tbody>
                {skills.map((skill) => (
                  <tr key={skill.skillId} className="profile-table-row">
                    <td className="profile-table-cell profile-table-cell-skill">{skill.skillName}</td>
                    <td className="profile-table-cell profile-table-cell-points">
                      <span className="profile-points-badge">
                        {skill.skillPoints} pt{skill.skillPoints !== 1 ? 's' : ''}
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
