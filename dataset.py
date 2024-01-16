import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset

class MultiImageDataset(Dataset):
    def labelsToGroundTruth(self, labels, LabelIndexMap):
        groundTruthVector = [0] * len(LabelIndexMap)
        labels = labels.split(',')

        for label in labels:
            if label in LabelIndexMap:
                groundTruthVector[LabelIndexMap[label]] = 1

        return groundTruthVector

    def __init__(self, rootDir, transform=None):
        self.transform = transform
        self.data = []

        labelList = ["onion", "onion2", "cheese", "cheese2", "tomato", "tomato2", "lettuce", "lettuce2",
            "patty", "patty2", "veggiePatty", "veggiePatty2", "friesS", "friesM", "friesL", "sticksS",
            "sticksM", "sticksL", "ringsS", "ringsM", "ringsL", "sodaS", "sodaM", "sodaL",
            "juiceS", "juiceM", "juiceL", "shakeS", "shakeM", "shakeL"]

        LabelIndexMap = {label: idx for idx, label in enumerate(labelList)}

        for dir in ["burger", "drink", "side"]:
            csv = pd.read_csv(f"{rootDir}/csv/{dir}.csv")
            for i in range(len(csv)):
                imageDir = f"{rootDir}/images/{dir}/{csv.iloc[i, 0]}"
                groundTruthVector = self.labelsToGroundTruth(csv.iloc[i, 1], LabelIndexMap)
                self.data.append((imageDir, groundTruthVector))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image = Image.open(self.data[idx][0])
        labels = self.data[idx][1]

        if self.transform:
            image = self.transform(image)

        labels = torch.tensor(labels, dtype=torch.float32)
        return image, labels

# dataloader = torch.utils.data.DataLoader(dataset, batch_size=4, shuffle=True)
#dataset = MultiImageDataset(r"C:\Users\ziggy\Documents\GitHub\bloxburg-fast-food-neural-net\labledData")
#print(len(dataset))
#print(dataset[346])
