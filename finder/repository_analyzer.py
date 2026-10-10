"""Repository architecture analyzer for technology detection and health indicators."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

# Standard mapping of aliases to canonical technology names
TECH_ALIASES: Dict[str, str] = {
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "react": "React",
    "reactjs": "React",
    "vue": "Vue",
    "vuejs": "Vue",
    "angular": "Angular",
    "next": "Next.js",
    "nextjs": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "express": "Express",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "java": "Java",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    ".net": ".NET",
    "dotnet": ".NET",
    "sql": "SQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "git": "Git",
    "github": "Git",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "graphql": "GraphQL",
    "testing": "Testing",
    "test": "Testing",
    "tests": "Testing",
    "pytest": "pytest",
    "unittest": "unittest",
    "jest": "Jest",
    "mocha": "Mocha",
    "vitest": "Vitest",
    "cypress": "Cypress",
    "playwright": "Playwright",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Machine Learning",
    "deep learning": "Deep Learning",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "pandas": "pandas",
    "numpy": "numpy",
    "documentation": "Documentation",
    "docs": "Documentation",
    "doc": "Documentation",
    "debugging": "Debugging",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "github actions": "GitHub Actions",
}

# Known file signatures to identify languages, frameworks, and tools
FILE_SIGNATURES: Dict[str, List[str]] = {
    # Build & Dependency files
    "pyproject.toml": ["Python", "Poetry/Flit/Build"],
    "requirements.txt": ["Python", "pip"],
    "Pipfile": ["Python", "Pipenv"],
    "setup.py": ["Python", "setuptools"],
    "package.json": ["JavaScript/TypeScript", "npm/yarn"],
    "pnpm-lock.yaml": ["pnpm"],
    "yarn.lock": ["yarn"],
    "tsconfig.json": ["TypeScript"],
    "pom.xml": ["Java", "Maven"],
    "build.gradle": ["Java/Kotlin", "Gradle"],
    "build.gradle.kts": ["Kotlin", "Gradle"],
    "go.mod": ["Go"],
    "Cargo.toml": ["Rust", "Cargo"],
    "CMakeLists.txt": ["C/C++", "CMake"],
    "Makefile": ["Make/C/C++"],
    "Dockerfile": ["Docker"],
    "docker-compose.yml": ["Docker Compose"],
    "docker-compose.yaml": ["Docker Compose"],
    # Config & CI
    ".github": ["GitHub Actions"],
    ".gitlab-ci.yml": ["GitLab CI"],
    ".eslintrc.json": ["ESLint"],
    ".prettierrc": ["Prettier"],
    "ruff.toml": ["Ruff"],
    "tox.ini": ["Tox"],
}

# Regex tech detection keywords for issue and README analysis
KEYWORD_TECH_MAP: Dict[str, str] = {
    r"\bpython\b": "Python",
    r"\bjavascript\b": "JavaScript",
    r"\btypescript\b": "TypeScript",
    r"\breact\b": "React",
    r"\bvue\b": "Vue",
    r"\bangular\b": "Angular",
    r"\bnext\.?js\b": "Next.js",
    r"\bnode(?:\.js)?\b": "Node.js",
    r"\bfastapi\b": "FastAPI",
    r"\bflask\b": "Flask",
    r"\bdjango\b": "Django",
    r"\bpytest\b": "pytest",
    r"\bjest\b": "Jest",
    r"\bunit\s*test(?:ing|s)?\b": "Testing",
    r"\btest(?:ing|s)?\b": "Testing",
    r"\brest\s*api(?:s)?\b": "REST APIs",
    r"\bgraphql\b": "GraphQL",
    r"\bsql\b": "SQL",
    r"\bpostgres(?:ql)?\b": "PostgreSQL",
    r"\bmysql\b": "MySQL",
    r"\bmongodb?\b": "MongoDB",
    r"\bdocker\b": "Docker",
    r"\bkubernetes|k8s\b": "Kubernetes",
    r"\bmachine\s*learning|ai|deep\s*learning\b": "Machine Learning",
    r"\bpytorch\b": "PyTorch",
    r"\btensorflow\b": "TensorFlow",
    r"\bscikit-learn|sklearn\b": "scikit-learn",
    r"\bpandas\b": "pandas",
    r"\bnumpy\b": "numpy",
    r"\bdocument(?:ation|s)?\b": "Documentation",
    r"\bdebug(?:ging)?\b": "Debugging",
    r"\bgit\b": "Git",
    r"\bci/cd|github\s*action(?:s)?\b": "CI/CD",
}


def normalize_skill(skill: str) -> str:
    """Normalize a user-entered skill or technology string to a canonical name."""
    clean = skill.strip().lower()
    return TECH_ALIASES.get(clean, skill.strip())


def normalize_skills_list(skills: List[str]) -> List[str]:
    """Normalize a list of skills, deduplicating while preserving clean casing."""
    normalized: List[str] = []
    seen: Set[str] = set()
    for s in skills:
        if not s or not s.strip():
            continue
        canon = normalize_skill(s)
        if canon.lower() not in seen:
            seen.add(canon.lower())
            normalized.append(canon)
    return normalized


def detect_technologies_from_text(text: str) -> List[str]:
    """Extract detected technologies and tools mentioned in text."""
    if not text:
        return []
    text_lower = text.lower()
    detected = set()

    for pattern, tech in KEYWORD_TECH_MAP.items():
        if re.search(pattern, text_lower):
            detected.add(tech)

    return sorted(list(detected))


class RepositoryAnalyzer:
    """Analyzes repository metadata, root structure, and documentation files."""

    def __init__(self, repo_metadata: Dict[str, Any], root_files: List[str], readme: Optional[str] = None, contributing: Optional[str] = None):
        self.metadata = repo_metadata
        self.root_files = root_files or []
        self.readme = readme
        self.contributing = contributing

    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive inspection of available repository artifacts."""
        detected_techs: Set[str] = set()
        primary_language = self.metadata.get("language") or "Unspecified"
        if primary_language != "Unspecified":
            detected_techs.add(primary_language)

        # Topics from GitHub repo
        for topic in self.metadata.get("topics", []):
            norm = normalize_skill(topic)
            detected_techs.add(norm)

        # Build files & config inspection
        detected_build_files: List[str] = []
        has_tests_dir = False
        has_docs_dir = False
        has_ci = False

        for f in self.root_files:
            f_lower = f.lower()
            if f in FILE_SIGNATURES:
                detected_build_files.append(f)
                for sign in FILE_SIGNATURES[f]:
                    detected_techs.add(sign)

            if "test" in f_lower:
                has_tests_dir = True
                detected_techs.add("Testing")
            if "doc" in f_lower:
                has_docs_dir = True
                detected_techs.add("Documentation")
            if f_lower in (".github", ".circleci", ".travis.yml"):
                has_ci = True
                detected_techs.add("CI/CD")

        # Inspect README if available
        readme_techs: List[str] = []
        if self.readme:
            readme_techs = detect_technologies_from_text(self.readme[:5000])
            for t in readme_techs:
                detected_techs.add(t)

        # Health indicators
        health = {
            "has_readme": self.readme is not None and len(self.readme.strip()) > 50,
            "has_contributing": self.contributing is not None and len(self.contributing.strip()) > 30,
            "has_license": self.metadata.get("license") not in ("Not specified", None, ""),
            "has_tests_indicator": has_tests_dir or any("test" in b.lower() for b in detected_build_files),
            "has_ci_indicator": has_ci,
            "stargazers": self.metadata.get("stargazers_count", 0),
            "forks": self.metadata.get("forks_count", 0),
            "open_issues_count": self.metadata.get("open_issues_count", 0),
            "archived": self.metadata.get("archived", False),
        }

        # Calculate a transparent health rating score (0 to 100)
        health_score = 0
        if health["has_readme"]:
            health_score += 25
        if health["has_contributing"]:
            health_score += 25
        if health["has_license"]:
            health_score += 20
        if health["has_tests_indicator"]:
            health_score += 15
        if health["has_ci_indicator"]:
            health_score += 15

        health["health_score"] = health_score

        # Note missing artifacts transparently
        missing_artifacts: List[str] = []
        if not health["has_readme"]:
            missing_artifacts.append("README file could not be found or is empty.")
        if not health["has_contributing"]:
            missing_artifacts.append("Contribution guide (CONTRIBUTING.md) was not detected.")
        if not health["has_license"]:
            missing_artifacts.append("No open-source license explicitly declared in repository metadata.")
        if not health["has_tests_indicator"]:
            missing_artifacts.append("No dedicated test directories or test configuration found in root.")

        return {
            "primary_language": primary_language,
            "detected_technologies": sorted(list(detected_techs)),
            "detected_build_files": detected_build_files,
            "health": health,
            "missing_artifacts": missing_artifacts,
            "inspected_files_count": len(self.root_files),
            "readme_available": self.readme is not None,
            "contributing_available": self.contributing is not None,
        }
