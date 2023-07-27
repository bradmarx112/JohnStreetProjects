import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores,record):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores,label='game score')
    plt.plot(mean_scores,label='mean score')
    plt.legend()
    plt.ylim(ymin=0)
    plt.text(len(scores)-1,scores[-1],str(scores[-1]))
    plt.text(len(mean_scores)-1,mean_scores[-1], str(mean_scores[-1]))
    # Add a text box to the plot
    plt.text(0.9, 3, f'Record: {record}', fontsize=12, bbox=dict(facecolor='yellow', alpha=0.5))