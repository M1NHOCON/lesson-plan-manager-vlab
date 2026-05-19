import { Link } from "react-router-dom";

function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(new Date(value));
}

export default function LessonPlanList({ items, onDelete }) {
  if (!items.length) {
    return <p className="empty-state">Nenhum plano encontrado.</p>;
  }

  return (
    <div className="lesson-list">
      {items.map((plan) => (
        <article className="lesson-card" key={plan.id}>
          <div className="lesson-card-main">
            <div>
              <h2>{plan.title}</h2>
              <p className="lesson-summary">{plan.summary}</p>
            </div>
            <div className="lesson-meta">
              <span>
                <strong>Disciplina:</strong> {plan.discipline}
              </span>
              <span>
                <strong>Data prevista:</strong> {formatDate(plan.planned_date)}
              </span>
              <span>
                <strong>Criado:</strong> {formatDate(plan.created_at)}
              </span>
            </div>
            <div className="tag-row">
              {(plan.tags || []).map((tag) => (
                <span className="tag-badge" key={tag}>
                  {tag}
                </span>
              ))}
            </div>
          </div>
          <div className="card-actions">
            <Link className="button secondary-button" to={`/lesson-plans/${plan.id}/edit`}>
              Editar
            </Link>
            <button className="danger-button" onClick={() => onDelete(plan)} type="button">
              Excluir
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}
