"""
JARVIS CLI

Komut satırı arayüzü.
"""

import argparse
import sys

from rich.console import Console

from jarvis import JARVIS
from jarvis.config import load_config
from jarvis.models import Language
from jarvis.prompt_library import PromptLibraryManager

console = Console()


def cmd_chat(args):
    """Metin tabanlı sohbet komutu"""
    jarvis = JARVIS()

    if args.message:
        # Tek mesaj gönder
        jarvis.chat(
            user_message=args.message,
            capture_screen=args.screen,
            speak_response=not args.no_voice,
        )
    else:
        # İnteraktif mod
        jarvis.interactive_mode()


def cmd_voice(args):
    """Sesli mod komutu"""
    jarvis = JARVIS()
    jarvis.voice_mode()


def cmd_prompt_list(args):
    """Prompt'ları listele"""
    config = load_config()
    manager = PromptLibraryManager(config.library_path)
    manager.list_prompts(show_table=True)


def cmd_prompt_add(args):
    """Yeni prompt ekle"""
    config = load_config()
    manager = PromptLibraryManager(config.library_path)

    # Eğer dosyadan okunacaksa
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            prompt_text = f.read()
    else:
        prompt_text = args.text

    if not prompt_text:
        console.print("[red]Hata: Prompt metni gerekli (--text veya --file)[/red]")
        sys.exit(1)

    # Dil parse
    language = Language.TR
    if args.language:
        try:
            language = Language(args.language)
        except ValueError:
            console.print(
                f"[yellow]Geçersiz dil: {args.language}, varsayılan TR kullanılıyor[/yellow]"
            )

    # Tags parse
    tags = []
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",")]

    manager.add_prompt(
        name=args.name,
        prompt_text=prompt_text,
        description=args.description,
        tags=tags,
        language=language,
    )


def cmd_prompt_delete(args):
    """Prompt sil"""
    config = load_config()
    manager = PromptLibraryManager(config.library_path)
    manager.delete_prompt(args.name)


def cmd_prompt_update(args):
    """Prompt güncelle"""
    config = load_config()
    manager = PromptLibraryManager(config.library_path)

    # Güncellenecek alanlar
    prompt_text = None
    if args.text:
        prompt_text = args.text
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            prompt_text = f.read()

    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",")]

    language = None
    if args.language:
        try:
            language = Language(args.language)
        except ValueError:
            console.print(f"[yellow]Geçersiz dil: {args.language}[/yellow]")

    manager.update_prompt(
        name=args.name,
        prompt_text=prompt_text,
        description=args.description,
        tags=tags,
        language=language,
    )


def cmd_prompt_activate(args):
    """Prompt'u aktif et"""
    config = load_config()
    manager = PromptLibraryManager(config.library_path)

    if args.name == "none":
        manager.set_active(None)
    else:
        manager.set_active(args.name)


def cmd_prompt_show(args):
    """Prompt detaylarını göster"""
    config = load_config()
    manager = PromptLibraryManager(config.library_path)

    prompt = manager.get_prompt(args.name)
    if not prompt:
        console.print(f"[red]'{args.name}' bulunamadı![/red]")
        sys.exit(1)

    from rich.panel import Panel

    content = f"""
[bold cyan]İsim:[/bold cyan] {prompt.name}
[bold cyan]Açıklama:[/bold cyan] {prompt.description or '-'}
[bold cyan]Etiketler:[/bold cyan] {', '.join(prompt.tags) or '-'}
[bold cyan]Dil:[/bold cyan] {prompt.language.value}
[bold cyan]Oluşturulma:[/bold cyan] {prompt.created_at}
[bold cyan]Güncellenme:[/bold cyan] {prompt.updated_at}

[bold yellow]Prompt Metni:[/bold yellow]
{prompt.prompt_text}
"""
    console.print(Panel(content, title=f"📄 {prompt.name}", border_style="cyan"))


def main():
    """Ana CLI entry point"""
    parser = argparse.ArgumentParser(
        description="JARVIS - Sesli + Ekran AI Asistan", prog="jarvis"
    )
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # Chat komutu
    chat_parser = subparsers.add_parser("chat", help="Sohbet et (text veya interaktif)")
    chat_parser.add_argument("-m", "--message", help="Tek mesaj gönder")
    chat_parser.add_argument(
        "-s", "--screen", action="store_true", help="Ekran görüntüsü ile sor"
    )
    chat_parser.add_argument(
        "--no-voice", action="store_true", help="Sesli cevap verme"
    )
    chat_parser.set_defaults(func=cmd_chat)

    # Voice komutu
    voice_parser = subparsers.add_parser("voice", help="Sesli mod başlat")
    voice_parser.set_defaults(func=cmd_voice)

    # Prompt yönetimi
    prompt_parser = subparsers.add_parser("prompt", help="Prompt kütüphanesi yönetimi")
    prompt_subparsers = prompt_parser.add_subparsers(dest="prompt_command")

    # Prompt list
    prompt_list = prompt_subparsers.add_parser("list", help="Prompt'ları listele")
    prompt_list.set_defaults(func=cmd_prompt_list)

    # Prompt add
    prompt_add = prompt_subparsers.add_parser("add", help="Yeni prompt ekle")
    prompt_add.add_argument("name", help="Prompt adı")
    prompt_add.add_argument("-t", "--text", help="Prompt metni")
    prompt_add.add_argument("-f", "--file", help="Prompt dosyası yolu")
    prompt_add.add_argument("-d", "--description", help="Açıklama")
    prompt_add.add_argument("-g", "--tags", help="Etiketler (virgülle ayrılmış)")
    prompt_add.add_argument(
        "-l", "--language", help="Dil (tr, en, tr+en)", default="tr"
    )
    prompt_add.set_defaults(func=cmd_prompt_add)

    # Prompt delete
    prompt_delete = prompt_subparsers.add_parser("delete", help="Prompt sil")
    prompt_delete.add_argument("name", help="Silinecek prompt adı")
    prompt_delete.set_defaults(func=cmd_prompt_delete)

    # Prompt update
    prompt_update = prompt_subparsers.add_parser("update", help="Prompt güncelle")
    prompt_update.add_argument("name", help="Güncellenecek prompt adı")
    prompt_update.add_argument("-t", "--text", help="Yeni prompt metni")
    prompt_update.add_argument("-f", "--file", help="Yeni prompt dosyası")
    prompt_update.add_argument("-d", "--description", help="Yeni açıklama")
    prompt_update.add_argument("-g", "--tags", help="Yeni etiketler")
    prompt_update.add_argument("-l", "--language", help="Yeni dil")
    prompt_update.set_defaults(func=cmd_prompt_update)

    # Prompt activate
    prompt_activate = prompt_subparsers.add_parser("activate", help="Prompt aktif et")
    prompt_activate.add_argument("name", help="Aktif edilecek prompt adı (none=genel)")
    prompt_activate.set_defaults(func=cmd_prompt_activate)

    # Prompt show
    prompt_show = prompt_subparsers.add_parser("show", help="Prompt detaylarını göster")
    prompt_show.add_argument("name", help="Gösterilecek prompt adı")
    prompt_show.set_defaults(func=cmd_prompt_show)

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Komutu çalıştır
    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as e:
            console.print(f"[red]Hata: {e}[/red]")
            if "--debug" in sys.argv:
                raise
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
