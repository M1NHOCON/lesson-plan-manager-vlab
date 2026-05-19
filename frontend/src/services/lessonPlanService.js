import api from "./api";

export async function listLessonPlans(params) {
  const response = await api.get("/lesson-plans", { params });
  return response.data;
}

export async function getLessonPlan(id) {
  const response = await api.get(`/lesson-plans/${id}`);
  return response.data;
}

export async function createLessonPlan(payload) {
  const response = await api.post("/lesson-plans", payload);
  return response.data;
}

export async function updateLessonPlan(id, payload) {
  const response = await api.put(`/lesson-plans/${id}`, payload);
  return response.data;
}

export async function deleteLessonPlan(id) {
  const response = await api.delete(`/lesson-plans/${id}`);
  return response.data;
}
