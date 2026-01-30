import matplotlib.pyplot as plt

def render_latex(formula, font_size=20, dpi=300, output_file='gravity_formula.png'):
    # Set up the figure
    fig = plt.figure(figsize=(6, 1))
    
    # Hide axes
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    
    # Render the formula
    # We use raw strings for LaTeX
    t = ax.text(0.5, 0.5, f"${formula}$",
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=font_size,
                color='#333333')
    
    # Save the figure
    # bbox_inches='tight' removes extra whitespace
    plt.savefig(output_file, dpi=dpi, transparent=True, bbox_inches='tight', pad_inches=0.1)
    print(f"Formula saved to {output_file}")

if __name__ == "__main__":
    # The formula from the paper
    # G_{chain} = \sum_{i=0}^{n} M_i \cdot e^{-0.5 \cdot d_i}
    formula = r"G_{chain} = \sum_{i=0}^{n} M_i \cdot e^{-0.5 \cdot d_i}"
    
    render_latex(formula, output_file='posts/super_bowl/assets/gravity_formula.png')
