import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Filters from "../components/Filters.jsx";
import LessonPlanList from "../components/LessonPlanList.jsx";
import Pagination from "../components/Pagination.jsx";
import { deleteLessonPlan, listLessonPlans } from "../services/lessonPlanService.js";

const DEFAULT_FILTERS = {
  search: "",
  discipline: "",
  tag: "",
  planned_date: "",
  sort_by: "created_at",
  order: "desc",
};

export default function LessonPlansPage() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [page, setPage] = useState(1);
  const [plans, setPlans] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function fetchPlans(nextPage = page, nextFilters = filters) {
    setLoading(true);
    setError("");

    try {
      const data = await listLessonPlans({
        ...nextFilters,
        page: nextPage,
        per_page: 10,
      });
      setPlans(data.items || []);
      setPagination(data.pagination);
    } catch (requestError) {
      setError(
        requestError?.response?.data?.error || "Não foi possível carregar os planos."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchPlans(1, filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleFilterSubmit(event) {
    event.preventDefault();
    setPage(1);
    fetchPlans(1, filters);
  }

  function handleClearFilters() {
    setFilters(DEFAULT_FILTERS);
    setPage(1);
    fetchPlans(1, DEFAULT_FILTERS);
  }

  async function handlePageChange(nextPage) {
    setPage(nextPage);
    await fetchPlans(nextPage, filters);
  }

  async function handleDelete(plan) {
    const confirmed = window.confirm(`Excluir o plano "${plan.title}"?`);
    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");
    try {
      await deleteLessonPlan(plan.id);
      setSuccess("Plano excluído com sucesso.");
      await fetchPlans(page, filters);
    } catch (requestError) {
      setError(requestError?.response?.data?.error || "Não foi possível excluir o plano.");
    }
  }

  return (
    <section className="list-panel">
      <div className="section-heading">
        <div>
          <h2>Planos de aula</h2>
          <p>Gerencie, filtre e acompanhe os planos cadastrados.</p>
        </div>
        <Link className="button" to="/lesson-plans/new">
          Novo plano
        </Link>
      </div>

      <Filters
        filters={filters}
        onChange={setFilters}
        onClear={handleClearFilters}
        onSubmit={handleFilterSubmit}
      />

      {error && <p className="message error-message">{error}</p>}
      {success && <p className="message success-message">{success}</p>}
      {loading ? (
        <p className="loading-state">Carregando planos...</p>
      ) : (
        <LessonPlanList items={plans} onDelete={handleDelete} />
      )}
      <Pagination pagination={pagination} onPageChange={handlePageChange} />
    </section>
  );
}
