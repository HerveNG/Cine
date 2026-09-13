import Link from "next/link";

const PROBLEMS = [
  "Structurer un projet audiovisuel de A à Z",
  "Rédiger des dossiers professionnels",
  "Comprendre les exigences des financeurs",
  "Trouver les bons fonds et ne pas rater les deadlines",
];

const PILLARS = [
  {
    title: "Project Development",
    description: "Structurez votre projet étape par étape, du concept au dossier complet.",
  },
  {
    title: "AI Writer",
    description:
      "Générez logline, synopsis, note d'intention et note de réalisation cohérents avec votre projet.",
  },
  {
    title: "Funding Intelligence",
    description: "Recherchez les opportunités de financement adaptées à votre projet.",
  },
  {
    title: "Matching",
    description:
      "Recevez un score de compatibilité indicatif entre votre projet et chaque opportunité.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <span className="font-display text-xl tracking-wide text-gold-soft">FilmFund Africa</span>
        <nav className="flex items-center gap-4">
          <Link href="/login" className="text-sm text-foreground/80 hover:text-gold-soft">
            Connexion
          </Link>
          <Link
            href="/register"
            className="rounded-md bg-gold px-4 py-2 text-sm font-medium text-[#14140f] transition-opacity hover:opacity-90"
          >
            Créer mon projet
          </Link>
        </nav>
      </header>

      <section className="mx-auto max-w-4xl px-6 pb-24 pt-16 text-center">
        <h1 className="font-display text-4xl leading-tight text-foreground md:text-6xl">
          Transformez votre idée en projet audiovisuel finançable.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted">
          Développez votre projet, créez votre dossier et découvrez les financements adaptés à
          votre film — pensé pour les auteurs, réalisateurs et producteurs d&apos;Afrique
          francophone.
        </p>
        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link
            href="/register"
            className="w-full rounded-md bg-gold px-6 py-3 text-center font-medium text-[#14140f] transition-opacity hover:opacity-90 sm:w-auto"
          >
            Créer mon projet
          </Link>
          <Link
            href="/login"
            className="w-full rounded-md border border-border-subtle px-6 py-3 text-center font-medium text-foreground/90 transition-colors hover:border-gold hover:text-gold-soft sm:w-auto"
          >
            Découvrir la plateforme
          </Link>
        </div>
      </section>

      <section className="border-t border-border-subtle bg-surface py-20">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="font-display text-2xl text-gold-soft">Le problème</h2>
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {PROBLEMS.map((problem) => (
              <div
                key={problem}
                className="rounded-lg border border-border-subtle bg-surface-raised p-5 text-foreground/90"
              >
                {problem}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="font-display text-2xl text-gold-soft">Ce que centralise FilmFund Africa</h2>
          <div className="mt-8 grid gap-6 sm:grid-cols-2">
            {PILLARS.map((pillar) => (
              <div
                key={pillar.title}
                className="rounded-xl border border-border-subtle bg-surface p-6"
              >
                <h3 className="font-display text-lg text-foreground">{pillar.title}</h3>
                <p className="mt-2 text-sm text-muted">{pillar.description}</p>
              </div>
            ))}
          </div>
          <p className="mt-6 text-sm text-muted">
            Le score de compatibilité est un indicateur d&apos;aide à la décision — il ne garantit
            jamais l&apos;obtention d&apos;un financement.
          </p>
        </div>
      </section>

      <footer className="border-t border-border-subtle py-10 text-center text-sm text-muted">
        © {new Date().getFullYear()} FilmFund Africa. Plateforme en développement (MVP).
      </footer>
    </div>
  );
}
