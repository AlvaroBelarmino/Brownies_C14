"""Envia um e-mail com o resumo do pipeline do GitHub Actions."""

from __future__ import annotations

import os
import smtplib
import sys
from email.message import EmailMessage


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_bool(name: str, default: bool) -> bool:
    value = _env(name)
    if not value:
        return default
    return value.lower() in {"1", "true", "yes", "on", "sim"}


def _env_list(name: str) -> list[str]:
    raw_value = _env(name)
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _overall_result(results: list[str]) -> str:
    normalized = [result or "unknown" for result in results]
    if any(result in {"failure", "cancelled", "timed_out"} for result in normalized):
        return "failure"
    if all(result == "success" for result in normalized):
        return "success"
    return "partial"


def _job_results() -> dict[str, str]:
    return {
        "test-backend": _env("TEST_BACKEND_RESULT", "unknown"),
        "lint-frontend": _env("LINT_FRONTEND_RESULT", "unknown"),
        "build": _env("BUILD_RESULT", "unknown"),
    }


def _build_subject(overall: str) -> str:
    repository = _env("GITHUB_REPOSITORY", "repositorio-desconhecido")
    workflow = _env("GITHUB_WORKFLOW", "workflow-desconhecido")
    branch = _env("GITHUB_REF_NAME", "branch-desconhecida")
    return f"[{overall.upper()}] {workflow} - {repository} ({branch})"


def _build_body(job_results: dict[str, str], overall: str) -> str:
    repository = _env("GITHUB_REPOSITORY", "repositorio-desconhecido")
    workflow = _env("GITHUB_WORKFLOW", "workflow-desconhecido")
    branch = _env("GITHUB_REF_NAME", "branch-desconhecida")
    actor = _env("GITHUB_ACTOR", "autor-desconhecido")
    event_name = _env("GITHUB_EVENT_NAME", "evento-desconhecido")
    run_number = _env("GITHUB_RUN_NUMBER", "0")
    sha = _env("GITHUB_SHA", "")[:7] or "sem-sha"
    server_url = _env("GITHUB_SERVER_URL", "https://github.com")
    run_id = _env("GITHUB_RUN_ID")

    lines = [
        f"Status geral: {overall.upper()}",
        f"Workflow: {workflow}",
        f"Repositorio: {repository}",
        f"Branch: {branch}",
        f"Evento: {event_name}",
        f"Autor: {actor}",
        f"Execucao: #{run_number}",
        f"Commit: {sha}",
        "",
        "Status dos jobs:",
    ]
    lines.extend(f"- {job_name}: {result}" for job_name, result in job_results.items())

    if run_id:
        lines.extend(
            [
                "",
                f"Detalhes da execucao: {server_url}/{repository}/actions/runs/{run_id}",
            ]
        )

    return "\n".join(lines)


def _smtp_port() -> int:
    raw_port = _env("SMTP_PORT", "587")
    try:
        return int(raw_port)
    except ValueError as exc:
        raise ValueError(f"SMTP_PORT invalido: {raw_port}") from exc


def main() -> int:
    smtp_host = _env("SMTP_HOST")
    smtp_username = _env("SMTP_USERNAME")
    smtp_password = _env("SMTP_PASSWORD")
    email_to = _env_list("NOTIFICATION_EMAIL_TO")
    email_from = _env("NOTIFICATION_EMAIL_FROM") or smtp_username

    missing = [
        name
        for name, value in {
            "SMTP_HOST": smtp_host,
            "SMTP_USERNAME": smtp_username,
            "SMTP_PASSWORD": smtp_password,
            "NOTIFICATION_EMAIL_TO": email_to,
        }.items()
        if not value
    ]
    if missing:
        print(
            "::warning::Configuracao de e-mail incompleta. "
            f"Variaveis ausentes: {', '.join(missing)}. Notificacao ignorada."
        )
        return 0

    job_results = _job_results()
    overall = _overall_result(list(job_results.values()))

    message = EmailMessage()
    message["Subject"] = _build_subject(overall)
    message["From"] = email_from
    message["To"] = ", ".join(email_to)
    message.set_content(_build_body(job_results, overall))

    try:
        with smtplib.SMTP(smtp_host, _smtp_port(), timeout=20) as smtp:
            smtp.ehlo()
            if _env_bool("SMTP_USE_TLS", True):
                smtp.starttls()
                smtp.ehlo()
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(message, to_addrs=email_to)
        print("Notificacao por e-mail enviada com sucesso.")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Falha ao enviar notificacao por e-mail: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
