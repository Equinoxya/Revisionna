import { useEffect, useRef } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../lib/AuthContext.jsx";
import ThemeToggle from "./ThemeToggle.jsx";

export function LiensLegaux() {
  return (
    <>
      <Link to="/mentions-legales">Mentions légales</Link>
      <Link to="/confidentialite">Confidentialité</Link>
      <Link to="/cgu">Conditions d&apos;utilisation</Link>
    </>
  );
}

export default function Layout() {
  const { user, chargement, logout } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const contenu = useRef(null);
  const premiere = useRef(true);

  // À chaque changement de page : retour en haut, et le focus suit (clavier, lecteur d'écran).
  useEffect(() => {
    if (premiere.current) {
      premiere.current = false;
      return;
    }
    window.scrollTo(0, 0);
    contenu.current?.focus({ preventScroll: true });
  }, [pathname]);

  async function deconnexion() {
    await logout();
    navigate("/connexion", { replace: true });
  }

  return (
    <div className="app">
      <a className="lien-evitement" href="#contenu">
        Aller au contenu
      </a>

      <header className="entete">
        <div className="entete-contenu">
          <Link to="/" className="marque">
            Revisionna
          </Link>

          {user && (
            <nav className="nav" aria-label="Navigation principale">
              <NavLink to="/" end>
                Bulletin
              </NavLink>
              <NavLink to="/cours">Sommaire</NavLink>
            </nav>
          )}

          <div className="outils">
            <ThemeToggle />
            {chargement ? null : user ? (
              <>
                <NavLink to="/compte">{user.username}</NavLink>
                <button type="button" className="lien-bouton" onClick={deconnexion}>
                  Se déconnecter
                </button>
              </>
            ) : (
              <Link to="/connexion">Se connecter</Link>
            )}
          </div>
        </div>
      </header>

      <main className="feuille" id="contenu" tabIndex={-1} ref={contenu}>
        <Outlet />
      </main>

      <footer className="pied">
        <div className="pied-contenu">
          <LiensLegaux />
          <span className="note-pied">Ni publicité, ni traceur, ni cookie tiers.</span>
        </div>
      </footer>
    </div>
  );
}
