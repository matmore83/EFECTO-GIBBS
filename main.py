"""Punto de entrada de la API de EFECTO-GIBBS."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import audio_router, router as senales_router

DIRECTORIO_WEB = Path(__file__).resolve().parent / "app" / "web"

app = FastAPI(
    title="EFECTO-GIBBS",
    description="Síntesis de funciones con discontinuidades periódicas y análisis del efecto Gibbs.",
    version="0.1.0",
)

app.include_router(senales_router)
app.include_router(audio_router)
app.mount("/static", StaticFiles(directory=DIRECTORIO_WEB / "static"), name="static")


@app.get("/", tags=["root"])
def raiz() -> FileResponse:
    """Sirve el frontend."""

    return FileResponse(DIRECTORIO_WEB / "index.html")


def main() -> None:
    """Levanta el servidor de desarrollo."""

    uvicorn.run("main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
