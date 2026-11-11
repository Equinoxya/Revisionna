import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../lib/AuthContext.jsx";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function deconnexion() {
    await logout();
    navigate("/connexion", { replace: true });
  }

  return (
    <div className="app">
      <header className="entete">
        <Link to="/" className="marque">
          <span aria-hidden="true">📚</span> Revisionna
        </Link>

        <nav className="nav">
          <NavLink to="/" end>
            Tableau de bord
          </NavLink>
          <NavLink to="/cours">Cours</NavLink>
        </nav>

        <div className="compte">
          {user && <span className="pseudo">{user.username}</span>}
          <button type="button" className="bouton-secondaire" onClick={deconnexion}>
            Deconnexion
          </button>
        </div>
      </header>

      <main className="contenu">
        <Outlet />
      </main>

      <footer className="pied">
        Flask + React + SQLAlchemy - projet de revision
      </footer>
    </div>
  );
}
