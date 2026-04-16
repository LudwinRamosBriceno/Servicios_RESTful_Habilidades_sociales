import { BookOpen, Package } from 'lucide-react'
import { cn } from '@/lib/utils'
import './catalog-view.css'

function StockBadge({ stock }) {
  if (stock === 0) {
    return <span className="stock-badge stock-badge-outofstock">Out of stock</span>
  }
  if (stock <= 15) {
    return (
      <span className="stock-badge stock-badge-low">
        {stock} pts — Low
      </span>
    )
  }
  return (
    <span className="stock-badge stock-badge-available">
      {stock} pts
    </span>
  )
}

export function CatalogView({ skills, onOrderClick }) {
  const totalAvailable = skills.filter((s) => s.stock > 0).length

  return (
    <main className="catalog-main">
      {/* Header */}
      <section className="catalog-header">
        <div className="catalog-header-content">
          <div className="catalog-header-title-row">
            <BookOpen className="w-5 h-5" style={{ color: '#2A5F7A' }} />
            <h2 className="catalog-header-title">Skills Catalog</h2>
          </div>
          <p className="catalog-header-subtitle">
            Browse all available soft skills. Click &ldquo;Order&rdquo; to acquire points.
          </p>
        </div>
        <div className="catalog-stats">
          <div className={`catalog-stat-card catalog-stat-card-total`}>
            <p className="catalog-stat-value catalog-stat-value-total">{skills.length}</p>
            <p className="catalog-stat-label">Total Skills</p>
          </div>
          <div className={`catalog-stat-card catalog-stat-card-instock`}>
            <p className="catalog-stat-value catalog-stat-value-instock">{totalAvailable}</p>
            <p className="catalog-stat-label">In Stock</p>
          </div>
        </div>
      </section>

      {/* Table */}
      <section className="catalog-section">
        <div className="catalog-section-header">
          <Package className="w-4 h-4" style={{ color: '#2A5F7A' }} />
          <h3 className="catalog-section-title">Available Skills</h3>
        </div>
        <div className="catalog-table-wrapper">
          <table className="catalog-table">
            <thead className="catalog-table-head">
              <tr>
                <th className="catalog-table-header">#</th>
                <th className="catalog-table-header catalog-table-skill">Skill Name</th>
                <th className="catalog-table-header catalog-table-header-stock">Stock</th>
                <th className="catalog-table-header catalog-table-header-action">Action</th>
              </tr>
            </thead>
            <tbody>
              {skills.map((skill, idx) => (
                <tr
                  key={skill.name}
                  className={cn(
                    'catalog-table-row',
                    skill.stock > 0 ? 'catalog-table-row-available' : 'catalog-table-row-unavailable',
                    idx % 2 !== 0 && 'catalog-table-row-alt'
                  )}
                >
                  <td className="catalog-table-cell catalog-table-cell-index">{String(idx + 1).padStart(2, '0')}</td>
                  <td className="catalog-table-cell catalog-table-skill">{skill.name}</td>
                  <td className="catalog-table-cell catalog-table-cell-stock">
                    <StockBadge stock={skill.stock} />
                  </td>
                  <td className="catalog-table-cell catalog-table-cell-action">
                    <button
                      onClick={() => onOrderClick(skill.name)}
                      disabled={skill.stock === 0}
                      className={cn(
                        'catalog-order-button',
                        skill.stock > 0 ? 'catalog-order-button-available' : 'catalog-order-button-unavailable'
                      )}
                    >
                      {skill.stock > 0 ? 'Order' : 'Unavailable'}
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
