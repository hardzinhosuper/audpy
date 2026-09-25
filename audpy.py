import sys
import os
import shutil

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError, ExtractorError
except ImportError:
    print("❌ O pacote 'yt-dlp' não está instalado.")
    print("   Instale com: pip install -U yt-dlp")
    sys.exit(1)


PASTA_PADRAO = r"" #Coloque a pasta que quiser 


def verificar_ffmpeg() -> bool:
    """Verifica se o ffmpeg está disponível no PATH."""
    return shutil.which("ffmpeg") is not None


def progresso(status: dict):
    if status.get("status") == "downloading":
        pct = status.get("_percent_str", "").strip()
        vel = status.get("_speed_str", "").strip()

        sys.stdout.write(
            f"\r⬇️  Baixando... {pct} ({vel})   "
        )
        sys.stdout.flush()

    elif status.get("status") == "finished":
        print("\n🔄 Convertendo para MP3...")


def montar_opcoes(pasta_destino: str) -> dict:
    return {
        "format": "bestaudio/best",

        "outtmpl": os.path.join(
            pasta_destino,
            "%(title).150B [%(id)s].%(ext)s"
        ),

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],

        "noplaylist": True,

        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,

        "restrictfilenames": False,

        "progress_hooks": [progresso],

        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
            }
        },

        "http_headers": {
            "User-Agent": (
                "com.google.android.youtube/19.09.37 "
                "(Linux; U; Android 14) gzip"
            )
        },
    }


def baixar_mp3(url: str, pasta_destino: str = PASTA_PADRAO) -> bool:
    """
    Baixa o áudio de um único vídeo do YouTube
    e salva como MP3.

    Retorna True em caso de sucesso.
    """

    os.makedirs(pasta_destino, exist_ok=True)

    opcoes = montar_opcoes(pasta_destino)

    try:
        with YoutubeDL(opcoes) as ydl:
            print(f"\n🎵 Processando: {url}")

            codigo_retorno = ydl.download([url])

        if codigo_retorno != 0:
            print("\n❌ O download não foi concluído.")
            return False

        print(
            "\n✅ Concluído! Arquivo salvo em: "
            f"{os.path.abspath(pasta_destino)}"
        )
        return True

    except DownloadError as e:
        print(f"\n❌ Erro ao baixar: {e}")

    except ExtractorError as e:
        print(f"\n❌ Erro ao extrair informações: {e}")

    except KeyboardInterrupt:
        print("\n⚠️ Download cancelado pelo usuário.")

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

    return False


def baixar_varias(quantidade: int, pasta_destino: str = PASTA_PADRAO):
    """Pede 'quantidade' links ao usuário e baixa todos, um por um."""

    links = []
    for numero in range(quantidade):
        link = input(f"Digite o link da música {numero + 1}: ").strip()
        links.append(link)

    print(f"\n📋 {len(links)} link(s) recebido(s)!")

    for link in links:
        if link:
            baixar_mp3(link, pasta_destino)


def loop_principal():

    if not verificar_ffmpeg():
        print("⚠️ AVISO: ffmpeg não foi encontrado no PATH.")
        print("   A conversão para MP3 vai falhar sem ele.")
        print("   Instale o ffmpeg antes de continuar.\n")

    print(f"📁 Pasta de destino: {PASTA_PADRAO}\n")

    # Se um link foi passado como argumento na linha de comando, baixa direto.
    if len(sys.argv) > 1:
        baixar_mp3(sys.argv[1])
        return

    # Pergunta se o usuário quer baixar em lote (quantidade fixa) ou no modo livre.
    resposta = input(
        "Quer informar quantas músicas vai baixar de uma vez? (s/N): "
    ).strip().lower()

    if resposta == "s":
        try:
            quantidade = int(input("Quantas músicas você quer baixar? (1-40): "))
        except ValueError:
            print("❌ Valor inválido. Voltando ao modo de links avulsos.\n")
        else:
            if quantidade < 1 or quantidade > 40:
                print("❌ Escolha uma quantidade entre 1 e 40.")
            else:
                baixar_varias(quantidade)
                return

    print("\nDigite os links um por um (ou 'sair' para encerrar):\n")

    while True:

        try:
            link = input().strip()

        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando... até a próxima! 🎧")
            break

        if link.lower() in ("sair", "exit", "quit", ""):
            print("Encerrando... até a próxima! 🎧")
            break

        if not link.lower().startswith(("http://", "https://")):
            print("⚠️ Isso não parece uma URL válida.")
            continue

        baixar_mp3(link)


if __name__ == "__main__":
    loop_principal()
