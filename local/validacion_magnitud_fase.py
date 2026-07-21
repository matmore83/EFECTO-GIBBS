import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.fourier_series import (
    magnitud_fase_diente_sierra,
    magnitud_fase_pulso,
    magnitud_fase_triangular,
)

ARMONICOS = 10
AMPLITUD = 1.0


def imprimir_resultados(nombre, A, phi):
    print("\n" + "=" * 60)
    print(nombre)
    print("=" * 60)

    print(f"{'n':>3} {'Magnitud':>12} {'Fase [rad]':>12}")

    for n, (amp, fase) in enumerate(zip(A, phi), start=1):
        print(f"{n:3d} {amp:12.6f} {fase:12.6f}")


def main():

    A, phi = magnitud_fase_pulso(
        amplitud=AMPLITUD,
        armonicos=ARMONICOS,
    )

    imprimir_resultados(
        "PULSO",
        A,
        phi,
    )

    A, phi = magnitud_fase_diente_sierra(
        amplitud=AMPLITUD,
        armonicos=ARMONICOS,
    )

    imprimir_resultados(
        "DIENTE DE SIERRA",
        A,
        phi,
    )

    A, phi = magnitud_fase_triangular(
        amplitud=AMPLITUD,
        armonicos=ARMONICOS,
    )

    imprimir_resultados("TRIANGULAR", A, phi)


if __name__ == "__main__":
    main()
