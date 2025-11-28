import { posts } from '../data/posts.js';

export function Archive() {
    const postList = posts.map(post => `
    <div style="margin-bottom: var(--spacing-lg); padding-bottom: var(--spacing-lg); border-bottom: 1px dashed var(--color-border);">
      <h3 style="margin-bottom: var(--spacing-xs);">
        <a href="/post/${post.id}" style="text-decoration: none; color: var(--color-primary);">${post.title}</a>
      </h3>
      <div style="font-size: 0.9rem; color: #666; margin-bottom: var(--spacing-sm);">
        ${post.date}
      </div>
      <p>${post.summary}</p>
    </div>
  `).join('');

    return `
    <div class="container">
      <section style="max-width: 800px; margin: 0 auto; padding: var(--spacing-xl) 0;">
        <h2 style="font-size: 2.5rem; margin-bottom: var(--spacing-lg); text-align: center;">The Archives</h2>
        
        <div style="background: white; padding: var(--spacing-xl); border: 1px solid var(--color-border); box-shadow: 5px 5px 15px rgba(0,0,0,0.05);">
          ${postList}
        </div>
      </section>
    </div>
  `;
}
