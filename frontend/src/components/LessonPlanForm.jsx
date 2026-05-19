import { Link } from "react-router-dom";
import { useMemo, useState } from "react";

import { getAiRecommendations } from "../services/aiService";

const EMPTY_FORM = {
  title: "",
  objective: "",
  summary: "",
  planned_date: "",
  discipline: "",
  contents: "",
  support_resources: "",
  tags: "",
};

function toLines(value) {
  return Array.isArray(value) ? value.join("\n") : value || "";
}

function fromLines(value) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function buildInitialForm(initialData) {
  if (!initialData) {
    return EMPTY_FORM;
  }

  return {
    title: initialData.title || "",
    objective: initialData.objective || "",
    summary: initialData.summary || "",
    planned_date: initialData.planned_date || "",
    discipline: initialData.discipline || "",
    contents: toLines(initialData.contents),
    support_resources: toLines(initialData.support_resources),
    tags: toLines(initialData.tags),
  };
}

function formatAiSource(source) {
  const labels = {
    gemini: "Gemini",
    mock: "Mock",
    openai: "OpenAI",
  };

  return labels[source] || source;
}

export default function LessonPlanForm({ initialData, mode, onSubmit }) {
  const [form, setForm] = useState(() => buildInitialForm(initialData));
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState("");
  const [aiError, setAiError] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSource, setAiSource] = useState("");
  const [aiGenerated, setAiGenerated] = useState(false);
  const [relatedTopics, setRelatedTopics] = useState([]);

  const title = mode === "edit" ? "Editar plano de aula" : "Novo plano de aula";
  const submitText = "Salvar plano";

  const requiredFields = useMemo(
    () => ({
      title: "Título obrigatório",
      objective: "Objetivo obrigatório",
      summary: "Ementa/Resumo obrigatório",
      planned_date: "Data prevista obrigatória",
      discipline: "Disciplina obrigatória",
    }),
    []
  );

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: "" }));
  }

  function validateRequired(fields) {
    const nextErrors = {};

    Object.entries(fields).forEach(([field, message]) => {
      if (!form[field]?.trim()) {
        nextErrors[field] = message;
      }
    });

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  function toPayload() {
    return {
      title: form.title.trim(),
      objective: form.objective.trim(),
      summary: form.summary.trim(),
      planned_date: form.planned_date,
      discipline: form.discipline.trim(),
      contents: fromLines(form.contents),
      support_resources: fromLines(form.support_resources),
      tags: fromLines(form.tags),
    };
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus("");

    if (!validateRequired(requiredFields)) {
      return;
    }

    try {
      await onSubmit(toPayload());
      setStatus("Plano salvo com sucesso.");
    } catch (error) {
      setStatus(error?.response?.data?.error || "Não foi possível salvar o plano.");
    }
  }

  async function handleAiRecommendations() {
    setAiError("");
    setAiSource("");
    setAiGenerated(false);
    setRelatedTopics([]);

    if (
      !validateRequired({
        title: "Título obrigatório para usar IA",
        discipline: "Disciplina obrigatória para usar IA",
        summary: "Ementa/Resumo obrigatório para usar IA",
      })
    ) {
      return;
    }

    setAiLoading(true);
    try {
      const recommendations = await getAiRecommendations({
        title: form.title.trim(),
        discipline: form.discipline.trim(),
        summary: form.summary.trim(),
      });

      setForm((current) => ({
        ...current,
        contents: toLines(recommendations.contents),
        tags: toLines(recommendations.tags),
      }));
      setRelatedTopics(recommendations.related_topics || []);
      setAiSource(recommendations.source || "");
      setAiGenerated(true);
    } catch (error) {
      setAiError(
        error?.response?.data?.error ||
          "Não foi possível gerar recomendações agora. Tente novamente."
      );
    } finally {
      setAiLoading(false);
    }
  }

  return (
    <section className="form-panel">
      <div className="section-heading">
        <div>
          <h2>{title}</h2>
          <p>Preencha os dados do plano e use a assistência para acelerar a organização.</p>
        </div>
      </div>

      <form className="lesson-form" onSubmit={handleSubmit}>
        <label className="field-title">
          Título
          <input name="title" onChange={updateField} value={form.title} />
          {errors.title && <span className="field-error">{errors.title}</span>}
        </label>

        <label className="field-discipline">
          Disciplina
          <input name="discipline" onChange={updateField} value={form.discipline} />
          {errors.discipline && <span className="field-error">{errors.discipline}</span>}
        </label>

        <label className="field-date">
          Data prevista
          <input
            name="planned_date"
            onChange={updateField}
            type="date"
            value={form.planned_date}
          />
          {errors.planned_date && <span className="field-error">{errors.planned_date}</span>}
        </label>

        <label className="field-full">
          Objetivo
          <textarea name="objective" onChange={updateField} rows="3" value={form.objective} />
          {errors.objective && <span className="field-error">{errors.objective}</span>}
        </label>

        <label className="field-full">
          Ementa/Resumo
          <textarea name="summary" onChange={updateField} rows="4" value={form.summary} />
          {errors.summary && <span className="field-error">{errors.summary}</span>}
        </label>

        <div className="ai-box">
          <div>
            <h3>Assistência com IA</h3>
            <p>Gere sugestões com base no título, disciplina e ementa/resumo.</p>
          </div>
          <button
            className="secondary-button"
            disabled={aiLoading}
            onClick={handleAiRecommendations}
            type="button"
          >
            {aiLoading ? "Gerando..." : "Gerar recomendações com IA"}
          </button>
          {aiError && <p className="message error-message">{aiError}</p>}
          {aiSource && (
            <p className="message success-message">Fonte da IA: {formatAiSource(aiSource)}</p>
          )}
          {aiGenerated && form.contents && (
            <div className="ai-suggestions">
              <h4>Conteúdos sugeridos</h4>
              <ul>
                {fromLines(form.contents).map((content) => (
                  <li key={content}>{content}</li>
                ))}
              </ul>
            </div>
          )}
          {relatedTopics.length > 0 && (
            <div className="ai-suggestions">
              <h4>Tópicos relacionados</h4>
              <ul>
                {relatedTopics.map((topic) => (
                  <li key={topic}>{topic}</li>
                ))}
              </ul>
            </div>
          )}
          {aiGenerated && form.tags && (
            <div className="ai-suggestions">
              <h4>Tags sugeridas</h4>
              <div className="tag-row">
                {fromLines(form.tags).map((tag) => (
                  <span className="tag-badge" key={tag}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <label>
          Conteúdos (um por linha)
          <textarea name="contents" onChange={updateField} rows="5" value={form.contents} />
        </label>

        <label>
          Recursos de apoio (um por linha)
          <textarea
            name="support_resources"
            onChange={updateField}
            rows="4"
            value={form.support_resources}
          />
        </label>

        <label className="field-full">
          Tags (uma por linha)
          <textarea name="tags" onChange={updateField} rows="4" value={form.tags} />
        </label>

        {status && (
          <p className={`message ${status.includes("sucesso") ? "success-message" : "error-message"}`}>
            {status}
          </p>
        )}

        <div className="form-actions">
          <Link className="button ghost-button" to="/">
            Cancelar
          </Link>
          <button type="submit">{submitText}</button>
        </div>
      </form>
    </section>
  );
}
