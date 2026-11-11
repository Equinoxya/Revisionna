import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Bulletin from "./pages/Bulletin.jsx";
import Compte from "./pages/Compte.jsx";
import Connexion from "./pages/Connexion.jsx";
import Cours from "./pages/Cours.jsx";
import Exercice from "./pages/Exercice.jsx";
import Inscription from "./pages/Inscription.jsx";
import Lecon from "./pages/Lecon.jsx";
import Sommaire from "./pages/Sommaire.jsx";
import Conditions from "./pages/legal/Conditions.jsx";
import Confidentialite from "./pages/legal/Confidentialite.jsx";
import MentionsLegales from "./pages/legal/MentionsLegales.jsx";

const prive = (page) => <ProtectedRoute>{page}</ProtectedRoute>;

export default function App() {
  return (
    <Routes>
      <Route path="/connexion" element={<Connexion />} />
      <Route path="/inscription" element={<Inscription />} />

      <Route element={<Layout />}>
        <Route path="/" element={prive(<Bulletin />)} />
        <Route path="/cours" element={prive(<Sommaire />)} />
        <Route path="/cours/:coursSlug" element={prive(<Cours />)} />
        <Route path="/cours/:coursSlug/lecons/:leconSlug" element={prive(<Lecon />)} />
        <Route path="/cours/:coursSlug/exercices/:exerciceSlug" element={prive(<Exercice />)} />
        <Route path="/compte" element={prive(<Compte />)} />

        {/* Pages publiques : lisibles sans compte. */}
        <Route path="/mentions-legales" element={<MentionsLegales />} />
        <Route path="/confidentialite" element={<Confidentialite />} />
        <Route path="/cgu" element={<Conditions />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
