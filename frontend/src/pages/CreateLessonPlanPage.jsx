import { useNavigate } from "react-router-dom";

import LessonPlanForm from "../components/LessonPlanForm.jsx";
import { createLessonPlan } from "../services/lessonPlanService.js";

export default function CreateLessonPlanPage() {
  const navigate = useNavigate();

  async function handleSubmit(payload) {
    await createLessonPlan(payload);
    setTimeout(() => navigate("/"), 600);
  }

  return <LessonPlanForm mode="create" onSubmit={handleSubmit} />;
}
