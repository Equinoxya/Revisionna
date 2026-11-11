import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Connexion from "./pages/Connexion.jsx";
import Cours from "./pages/Cours.jsx";
import Catalogue from "./pages/Catalogue.jsx";
import Exercice from "./pages/Exercice.jsx";
import Inscription from "./pages/Inscription.jsx";
import Lecon from "./pages/Lecon.jsx";
import TableauDeBord from "./pages/TableauDeBord.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/connexion" element={<Connexion />} />
      <Route path="/inscription" element={<Inscription />} />

      <Route element={<Layout />}>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <TableauDeBord />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cours"
          element={
            <ProtectedRoute>
              <Catalogue />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cours/:coursSlug"
          element={
            <ProtectedRoute>
              <Cours />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cours/:coursSlug/lecons/:leconSlug"
          element={
            <ProtectedRoute>
              <Lecon />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cours/:coursSlug/exercices/:exerciceSlug"
          element={
            <ProtectedRoute>
              <Exercice />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
