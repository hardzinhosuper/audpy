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


def verificar_ffmpeg() -> bool:
    """Verifica se o ffmpeg está disponível no PATH."""
    return shutil.which("ffmpeg") is not None


def montar_opcoes(pasta_destino: str, baixar_playlist: bool) -> dict:
    return {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(pasta_destino, "%(title).150B [%(id)s].%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "noplaylist": not baixar_playlist,
        "quiet": True,
        "no_warnings": True,
        # Só ignora erros individuais quando é playlist (1 item ruim não derruba o resto).
        # Em vídeo único, deixamos o erro aparecer de verdade.
        "ignoreerrors": baixar_playlist,
        "restrictfilenames": False,
        "progress_hooks": [progresso],
        # Tenta contornar bloqueios 403 usando o client "android" do YouTube,
        # que costuma sofrer menos com restrições que o client "web".
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
            }
        },
        "http_headers": {
            "User-Agent": "com.google.android.youtube/19.09.37 (Linux; U; Android 14) gzip"
        },
    }


def progresso(status: dict):
    if status.get("status") == "downloading":
        pct = status.get("_percent_str", "").strip()
        vel = status.get("_speed_str", "").strip()
        sys.stdout.write(f"\r⬇️  Baixando... {pct} ({vel})   ")
        sys.stdout.flush()
    elif status.get("status") == "finished":
        print("\n🔄 Convertendo para MP3...")


def eh_playlist(url: str) -> bool:
    return "list=" in url or "/playlist" in url


def baixar_mp3(url: str, pasta_destino: str = "downloads") -> bool:
    """
    Baixa o áudio de um vídeo (ou playlist) do YouTube e salva como MP3.

    Retorna True se concluiu sem levantar erro fatal, False caso contrário.
    """
    os.makedirs(pasta_destino, exist_ok=True)

    baixar_playlist = False
    if eh_playlist(url):
        resp = input("🔗 Este link parece ser uma playlist. Baixar todos os itens? (s/N): ").strip().lower()
        baixar_playlist = resp == "s"

    opcoes = montar_opcoes(pasta_destino, baixar_playlist)

    try:
        with YoutubeDL(opcoes) as ydl:
            print(f"\n🎵 Processando: {url}")
            codigo_retorno = ydl.download([url])

        # ydl.download retorna 0 em caso de sucesso e != 0 se algo falhou.
        # Isso evita mostrar "Concluído" quando na verdade nada foi baixado.
        if codigo_retorno != 0:
            print("\n❌ O download não foi concluído (veja o erro acima, se houver).")
            return False

        print(f"\n✅ Concluído! Arquivo(s) salvo(s) em: {os.path.abspath(pasta_destino)}")
        return True

    except DownloadError as e:
        print(f"\n❌ Erro ao baixar (link inválido, vídeo privado/removido, ou restrição): {e}")
    except ExtractorError as e:
        print(f"\n❌ Não foi possível extrair informações do vídeo: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  Download cancelado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

    return False


def loop_principal():
    print("=" * 50)
    print("  Baixador de Músicas do YouTube (MP3)")
    print("=" * 50)
    print("Digite 'sair' a qualquer momento para fechar o programa.\n")

    if not verificar_ffmpeg():
        print("⚠️  AVISO: ffmpeg não foi encontrado no PATH.")
        print("   A conversão para MP3 vai falhar sem ele.")
        print("   Instale o ffmpeg antes de continuar.\n")

    # Se o usuário passar uma URL direto pela linha de comando,
    # baixa ela primeiro antes de entrar no loop
    if len(sys.argv) > 1:
        baixar_mp3(sys.argv[1])

    while True:
        try:
            link = input("\nCole a URL do vídeo do YouTube (ou 'sair'): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando... até a próxima! 🎧")
            break

        if link.lower() in ("sair", "exit", "quit", ""):
            print("Encerrando... até a próxima! 🎧")
            break

        if not link.lower().startswith(("http://", "https://")):
            print("⚠️  Isso não parece uma URL válida. Tente novamente.")
            continue

        # Qualquer falha aqui já é tratada dentro de baixar_mp3,
        # então o loop nunca quebra e sempre volta a pedir outro link.
        baixar_mp3(link)


if __name__ == "__main__":
    loop_principal()