export default function Pagination({ pagination, onPageChange }) {
  if (!pagination || pagination.total_pages <= 1) {
    return null;
  }

  return (
    <div className="pagination">
      <button
        disabled={!pagination.has_prev}
        onClick={() => onPageChange(pagination.page - 1)}
        type="button"
      >
        Anterior
      </button>
      <span>
        Página {pagination.page} de {pagination.total_pages} ({pagination.total_items} itens)
      </span>
      <button
        disabled={!pagination.has_next}
        onClick={() => onPageChange(pagination.page + 1)}
        type="button"
      >
        Próxima
      </button>
    </div>
  );
}
