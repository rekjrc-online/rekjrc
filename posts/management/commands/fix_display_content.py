from django.core.management.base import BaseCommand
from posts.models import Post
from django.utils.html import escape
import re

def sanitize_post_content(raw: str) -> str:
    if not raw:
        return ""

    # Strip all HTML tags
    raw = re.sub(r"<.*?>", "", raw)

    # Escape anything remaining
    raw = escape(raw)

    # Auto-link URLs
    url_pattern = re.compile(r"(https?://[^\s]+)")
    return url_pattern.sub(r'<a href="\1" target="_blank" onclick="event.stopPropagation();">\1</a>', raw)

class Command(BaseCommand):
    help = "Fix missing display_content on posts"

    def handle(self, *args, **options):
        posts = Post.objects.filter(display_content__isnull=True).exclude(content="")
        count = posts.count()

        for p in posts:
            p.display_content = sanitize_post_content(p.content)
            p.save(update_fields=["display_content"])

        self.stdout.write(self.style.SUCCESS(f"Fixed {count} posts."))
