import api from "./api";

export async function getAiRecommendations(payload) {
  const response = await api.post("/ai/recommendations", payload);
  return response.data;
}
