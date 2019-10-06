

from torchvision import models, transforms

# Create new class definitions for
# - loading data from Image folder (class1, class2, class3...) with optional subset of classes
# - split data into train and val subsets

from torch.utils.data import Dataset
from torchvision.datasets.folder import DatasetFolder, default_loader, IMG_EXTENSIONS, make_dataset, pil_loader


class ImageFolderWithClassSubset(DatasetFolder):
    '''
    Subclass of DatasetFolder that accept subset of classes defined by classes_subset.
    If classes_subset = None, then all classes are choosen.
    '''

    def __init__(self, root, classes_subset=None):
        super().__init__(root, loader=pil_loader, extensions=IMG_EXTENSIONS)
        if classes_subset:
           # check if the classes in classes_subset are part of available classes detected by DatasetFolder in the root folder
            if all([_ in self.classes for _ in classes_subset]):
                classes, class_to_idx = classes_subset, {
                    classes_subset[i]: i for i in range(len(classes_subset))}
                samples = make_dataset(
                    self.root, class_to_idx, extensions=IMG_EXTENSIONS)
                self.classes = classes
                self.class_to_idx = class_to_idx
                self.samples = samples
                self.targets = [s[1] for s in samples]
            else:
                print("Certain Class in classes_subset is not available in possible classes. Check your classes_subset. Choosing all classes instead")


class TrainValSubsets(Dataset):
    '''
    Subset a dataset based on indices
    '''

    def __init__(self, dataset, indices, transforms=None):
        self.subset = dataset
        self.indices = indices
        self.transforms = transforms

        if not self.transforms:
            self.transforms = transforms.Compose([transforms.ToTensor()])
        else:
            self.transforms = transforms

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        sample = self.subset[self.indices[idx]]
        return (self.transforms(sample[0]), sample[1])

# Load data

data_root = Path('../Data')
all_data = ImageFolderWithClassSubset(root=data_root, classes_subset=[
                                      'arts_and_crafts', 'mid-century-modern', 'rustic', 'traditional'])
print(all_data)
print(f"Classes: {all_data.classes}")
print(f"Class Mapping: {all_data.class_to_idx}")

# Create indices for train and val data based on ranom split on whole dataset
# Create random split and create indices for train and val
idx = {}
# torch.manual_seed(1)
rand_idx = torch.randperm(len(all_data))
val_pct = .2
split = int(val_pct*len(rand_idx))
idx['val'] = rand_idx[:split]
idx['train'] = rand_idx[split:]

# Define Transforms on train and val data


imagenet_stats = ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])

trfms = {}
trfms['train'] = transforms.Compose([transforms.RandomResizedCrop(224),
                                     transforms.RandomHorizontalFlip(),
                                     transforms.RandomRotation(10),
                                     transforms.ToTensor(),
                                     transforms.Normalize(*imagenet_stats)])

trfms['val'] = transforms.Compose([transforms.Resize((224, 224)),
                                   transforms.ToTensor(),
                                   transforms.Normalize(*imagenet_stats)])


# Create Train and val  datasets and dataloaders

datasets = {}  # Holds datasets
dataloaders = {}  # Holds dataloaders
BATCH_SIZE = 32

for datatype in ['train', 'val']:

    # Dataset
    datasets[datatype] = TrainValSubsets(
        all_data, idx[datatype],  transforms=trfms[datatype])

    # Dataloader
    dataloaders[datatype] = torch.utils.data.DataLoader(
        datasets[datatype], BATCH_SIZE, num_workers=4, shuffle=True)

# Define a data dict that holds dataloaders, datasets, mappings, transforms, normalizing stats etc.

data = {}
data['norm_stats'] = imagenet_stats
data['ds'] = datasets
data['dl'] = dataloaders
data['classes'] = all_data.classes
data['tfms'] = trfms
data['maping'] = all_data.class_to_idx

# lets check the size of the train image dataset
print(f"Train size: {len(data['ds']['train'])}")

# Test the first image on val image_dataset
print(f"Val size: {len(data['ds']['val'])}")
