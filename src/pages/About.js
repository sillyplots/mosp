export function About() {
    return `
    <div class="container">
      <section style="max-width: 800px; margin: 0 auto; padding: var(--spacing-xl) 0;">
        <h2 style="font-size: 2.5rem; margin-bottom: var(--spacing-lg); text-align: center;">About the Ministry</h2>
        
        <div style="background: white; padding: var(--spacing-xl); border: 1px solid var(--color-border); box-shadow: 5px 5px 15px rgba(0,0,0,0.05);">
          <p style="font-size: 1.2rem; margin-bottom: var(--spacing-md);">
            The Ministry of Silly Plots was founded in 2024 with a singular vision: <strong>Data is too important to be taken seriously.</strong>
          </p>

          <p style="margin-bottom: var(--spacing-md);">
            Our team of uncertified data scientists uses state-of-the-art random number generators and "gut feelings" to uncover correlations that statistically significant models often miss (because they aren't there).
          </p>

          <h3 style="margin-top: var(--spacing-lg); margin-bottom: var(--spacing-md);">Our Mission</h3>
          <ul style="list-style-type: disc; padding-left: var(--spacing-lg); margin-bottom: var(--spacing-lg);">
            <li style="margin-bottom: var(--spacing-sm);">To confuse causation with correlation at every opportunity.</li>
            <li style="margin-bottom: var(--spacing-sm);">To create charts that look beautiful but convey zero information.</li>
            <li style="margin-bottom: var(--spacing-sm);">To ensure that no y-axis ever starts at zero.</li>
          </ul>

          <p style="font-style: italic; color: #666; text-align: center; margin-top: var(--spacing-xl);">
            "If the data doesn't fit the narrative, change the axis scale." <br>
            — The Minister
          </p>
        </div>
      </section>
    </div>
  `;
}
