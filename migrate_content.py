
import os
import re

POSTS_DIR = 'posts'

def migrate():
    # Walk existing posts
    for root, dirs, files in os.walk(POSTS_DIR):
        for file in files:
            if file == 'index.md':
                path = os.path.join(root, file)
                process_file(path)

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already migrated
    if content.startswith('---'):
        print(f"Skipping {path}, already has frontmatter")
        return

    # Extract title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled Post"

    # Determine permalink
    # posts/super_bowl/index.md -> /post/superbowl/
    parent_dir = os.path.basename(os.path.dirname(path))
    
    # Custom mapping for known posts
    if parent_dir == 'super_bowl':
        permalink = "/post/superbowl/"
    else:
        permalink = f"/post/{parent_dir}/"

    # Create Frontmatter
    safe_title = title.replace('"', '\\"')
    frontmatter = f"""---
layout: default
title: "{safe_title}"
permalink: {permalink}
---

"""
    
    # Prepend frontmatter
    new_content = frontmatter + content
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Migrated {path} -> {permalink}")

if __name__ == "__main__":
    migrate()
