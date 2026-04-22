import { BookOpen } from 'lucide-react'
import { cn } from '@/lib/utils'
import './catalog-view.css'

// Maneja la visualización del estado de stock de cada habilidad en el catálogo.
function StockBadge({ stock }) {
  // Sin existencia
  if (stock === 0) {
    return <span className="stock-badge stock-badge-outofstock">Sin existencia</span>
  }
  // Stock bajo
  if (stock <= 15) {
    return (
      <span className="stock-badge stock-badge-low">
        {stock} pts
      </span>
    )
  }
  // Stock disponible
  return (
    <span className="stock-badge stock-badge-available">
      {stock} pts
    </span>
  )
}

/**
 * Componente de vista del catálogo de habilidades.
 */
export function CatalogView({ skills, onOrderClick }) {

  // Renderizar la vista del catálogo
  return (
    <main className="catalog-main">
      
      {/* Encabezado */}
      <section className="catalog-header">
        <div className="catalog-header-content">
          <div className="catalog-header-title-row">
            <h2 className="catalog-header-title">Catálogo de Habilidades</h2>
          </div>
          <p className="catalog-header-subtitle">
            Explora todas las habilidades blandas disponibles. Haz clic en "Ordenar" para adquirir puntos.
          </p>
        </div>
      </section>

      {/* Table */}
      <section className="catalog-section">

        {/* Tabla de habilidades */}
        <div className="catalog-table-wrapper">
          <table className="catalog-table">

            {/* Encabezado de la tabla */}
            <thead className="catalog-table-head">
              <tr>
                <th className="catalog-table-header catalog-table-skill">Habilidad</th>
                <th className="catalog-table-header catalog-table-header-stock">Stock</th>
                <th className="catalog-table-header catalog-table-header-action">Acción</th>
              </tr>
            </thead>
            
            {/* Cuerpo de la tabla con habilidades */}
            <tbody>
              {skills.map((skill) => (
                
                // Filas de la tabla (nombre de habilidad, stock y botón de acción)
                <tr
                  key={skill.id}
                  className={cn(
                    'catalog-table-row',
                    skill.stock > 0 ? 'catalog-table-row-available' : 'catalog-table-row-unavailable',
                  )}
                >
                  {/* Celda de nombre de habilidad */}
                  <td className="catalog-table-cell catalog-table-skill">{skill.name}</td>

                  {/* Celda de stock con badge */}
                  <td className="catalog-table-cell catalog-table-cell-stock">
                    <StockBadge stock={skill.stock} />
                  </td>

                  {/* Celda de acción con botón de ordenar */}
                  <td className="catalog-table-cell catalog-table-cell-action">
                    <button
                      onClick={() => onOrderClick(skill.id)} // Llamar a la función de pedido con el id de la habilidad
                      disabled={skill.stock === 0}
                      className={cn(
                        'catalog-order-button',
                        skill.stock > 0 ? 'catalog-order-button-available' : 'catalog-order-button-unavailable'
                      )}
                    >
                      {skill.stock > 0 ? 'Ordenar' : 'No Disponible'}
                    </button>
                  </td>
                </tr>

              ))}
            </tbody>
            
          </table>

        </div>
      </section>
      
    </main>
  )
}
