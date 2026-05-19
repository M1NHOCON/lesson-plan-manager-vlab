import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import LessonPlanForm from "../components/LessonPlanForm.jsx";
import { getLessonPlan, updateLessonPlan } from "../services/lessonPlanService.js";

export default function EditLessonPlanPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchPlan() {
      setLoading(true);
      setError("");
      try {
        const data = await getLessonPlan(id);
        setPlan(data);
      } catch (requestError) {
        setError(requestError?.response?.data?.error || "Não foi possível carregar o plano.");
      } finally {
        setLoading(false);
      }
    }

    fetchPlan();
  }, [id]);

  async function handleSubmit(payload) {
    await updateLessonPlan(id, payload);
    setTimeout(() => navigate("/"), 600);
  }

  if (loading) {
    return <p className="loading-state">Carregando plano...</p>;
  }

  if (error) {
    return <p className="message error-message">{error}</p>;
  }

  return <LessonPlanForm initialData={plan} mode="edit" onSubmit={handleSubmit} />;
}
