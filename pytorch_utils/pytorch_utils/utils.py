from .imports import *
from .hooks import Hook



def show_batch(dataloader,classes,normalize_stats,plot_num=12):
    
    if not isinstance(dataloader, torch.utils.data.DataLoader):
        raise('dataloader argument not an instance of torch.utils.data.DataLoader')
        
    inputs, classes = next(iter(dataloader))

    classes = classes.tolist()

     # denormalization 
    if normalize_stats:
        mean, std = normalize_stats
        std = torch.tensor(std)
        mean = torch.tensor(mean)
        inputs = inputs.mul(std[None,:,None,None])+mean[None,:,None,None]

    plot_num = inputs.shape[0] if (plot_num > inputs.shape[0]) else plot_num
        
    ncols = 4
    nrows = math.ceil(plot_num/ncols)

    fig, ax = plt.subplots(nrows, ncols, figsize=(12,12))
    ax = ax.ravel()

    for img in range(plot_num):
        image = inputs[img,...].permute(1,2,0)  
        if image.shape[2] == 1: # If greyscale
            image = image.squeeze()
            image = torch.stack([image]*3, dim = 2)
        ax[img].imshow(image)
        ax[img].set_title(classes[img])

    for _ in ax:
        _.axis('off')


def plot_confusion_matrix(y_true, y_pred, classes,
                          normalize=False,
                          title=None,
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    fig, ax = plt.subplots(figsize=(8,8))
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]+1)-0.5,
           yticks=np.arange(cm.shape[0]+1)-0.5,
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    #ax.grid(which="minor", color='w', linestyle='-',linewidth=3)
    # ax.tick_params(which="minor", bottom = False, left=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    return ax


