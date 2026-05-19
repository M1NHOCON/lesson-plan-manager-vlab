const SORT_OPTIONS = [
  { value: "created_at", label: "Cadastro" },
  { value: "planned_date", label: "Data prevista" },
  { value: "title", label: "Título" },
];

export default function Filters({ filters, onChange, onSubmit, onClear }) {
  function updateField(event) {
    const { name, value } = event.target;
    onChange({ ...filters, [name]: value });
  }

  return (
    <form className="filters-bar" onSubmit={onSubmit}>
      <label>
        Busca
        <input
          name="search"
          onChange={updateField}
          placeholder="Título do plano"
          value={filters.search}
        />
      </label>

      <label>
        Disciplina
        <input
          name="discipline"
          onChange={updateField}
          placeholder="Redes"
          value={filters.discipline}
        />
      </label>

      <label>
        Tag
        <input name="tag" onChange={updateField} placeholder="OSPF" value={filters.tag} />
      </label>

      <label>
        Data prevista
        <input
          name="planned_date"
          onChange={updateField}
          type="date"
          value={filters.planned_date}
        />
      </label>

      <label>
        Ordenar por
        <select name="sort_by" onChange={updateField} value={filters.sort_by}>
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label>
        Ordem
        <select name="order" onChange={updateField} value={filters.order}>
          <option value="desc">Decrescente</option>
          <option value="asc">Crescente</option>
        </select>
      </label>

      <div className="filter-actions">
        <button type="submit">Aplicar</button>
        <button className="ghost-button" onClick={onClear} type="button">
          Limpar
        </button>
      </div>
    </form>
  );
}
