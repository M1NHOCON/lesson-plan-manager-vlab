import { Link, Route, Routes } from "react-router-dom";

import CreateLessonPlanPage from "./pages/CreateLessonPlanPage.jsx";
import EditLessonPlanPage from "./pages/EditLessonPlanPage.jsx";
import LessonPlansPage from "./pages/LessonPlansPage.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-block">
          <h1>
            <Link className="brand-link" to="/">
              Gerenciador de Planos de Aula
            </Link>
          </h1>
        </div>
        <nav>
          <Link to="/">Planos</Link>
          <Link className="primary-link" to="/lesson-plans/new">
            Novo plano
          </Link>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<LessonPlansPage />} />
          <Route path="/lesson-plans/new" element={<CreateLessonPlanPage />} />
          <Route path="/lesson-plans/:id/edit" element={<EditLessonPlanPage />} />
        </Routes>
      </main>

      <footer className="app-footer">V-LAB</footer>
    </div>
  );
}
