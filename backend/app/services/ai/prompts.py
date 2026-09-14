from app.models.document import DocumentType
from app.models.project import Project

SYSTEM_PROMPT = (
    "Tu es un scénariste-conseil spécialisé dans le développement de projets "
    "audiovisuels africains (documentaire, fiction, série). Tu écris en "
    "français, de façon concrète et professionnelle, sans emphase inutile. "
    "Tu réponds uniquement avec le texte demandé, sans titre ni "
    "introduction de type « Voici ... »."
)

_DOCUMENT_LABELS: dict[DocumentType, str] = {
    DocumentType.LOGLINE: "une logline (une à deux phrases percutantes résumant le projet)",
    DocumentType.SYNOPSIS_SHORT: "un synopsis court (environ 150 mots)",
    DocumentType.SYNOPSIS_LONG: "un synopsis long et détaillé (environ 500 mots)",
    DocumentType.NOTE_INTENTION: (
        "une note d'intention du réalisateur ou de la réalisatrice "
        "(pourquoi ce projet, quel regard, quel traitement)"
    ),
    DocumentType.TRAITEMENT: (
        "un traitement (découpage narratif détaillé du projet, séquence par séquence)"
    ),
    DocumentType.PITCH: "un pitch oral de présentation du projet (30 secondes à l'oral)",
}


def _project_context(project: Project) -> str:
    fields = {
        "Titre": project.title,
        "Type": project.project_type.value,
        "Genre": project.genre,
        "Pays": project.country,
        "Langue": project.language,
        "Durée (minutes)": project.duration_minutes,
        "Logline existante": project.logline,
        "Synopsis court existant": project.short_synopsis,
        "Synopsis long existant": project.long_synopsis,
        "Thème": project.theme,
        "Public cible": project.target_audience,
    }
    lines = [f"- {label} : {value}" for label, value in fields.items() if value]
    return "\n".join(lines)


def build_generation_prompt(
    project: Project, document_type: DocumentType, instructions: str | None
) -> str:
    parts = [
        f"Rédige {_DOCUMENT_LABELS[document_type]} pour le projet audiovisuel suivant :",
        _project_context(project),
    ]
    if instructions:
        parts.append(f"\nConsigne particulière de l'utilisateur : {instructions}")
    return "\n\n".join(parts)


def build_improve_prompt(
    project: Project, document_type: DocumentType, existing_content: str, instruction: str
) -> str:
    return (
        f"Voici {_DOCUMENT_LABELS[document_type]} déjà rédigé(e) pour ce projet :\n\n"
        f"{existing_content}\n\n"
        f"Contexte du projet :\n{_project_context(project)}\n\n"
        f"Réécris ce texte en tenant compte de cette consigne : {instruction}\n"
        "Renvoie uniquement le texte final réécrit."
    )


def build_shorten_prompt(
    project: Project, document_type: DocumentType, existing_content: str
) -> str:
    return (
        f"Voici {_DOCUMENT_LABELS[document_type]} déjà rédigé(e) pour ce projet :\n\n"
        f"{existing_content}\n\n"
        "Raccourcis ce texte d'environ moitié tout en conservant les informations "
        "essentielles et le ton. Renvoie uniquement le texte final raccourci."
    )
