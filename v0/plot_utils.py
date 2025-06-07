# plot_utils.py
import matplotlib.pyplot as plt
import seaborn as sns

# Plot a masked heatmap to visualize correlations between time series

def plot_heatmap(correlation_df, title="Correlation Matrix"):
    import numpy as np
    mask = np.triu(np.ones(correlation_df.shape), k=1)
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        correlation_df,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        cbar_kws={'label': 'Correlation coefficient'}
    )
    plt.title(title, fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.show()

# Plot a line graph of rolling correlation between two assets

def plot_rolling_correlation(rolling_corr, sym1, sym2, window):
    rolling_corr.plot(title=f"Rolling Correlation between {sym1} and {sym2} ({window}-day window)")
    plt.xlabel("Date")
    plt.ylabel("Correlation")
    plt.ylim(-1, 1)
    plt.grid(True)
    plt.tight_layout()
    plt.show()