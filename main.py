import pyautogui
import numpy as np
import cv2 as cv

centerPlus = (475, 1270) #For 2 and 4 items
leftPlus = (476, 1160) #For 3 items
plusColor = [100, 100, 100]

plusSideOffset = 205
plusArmOsset = 22 #There should be no black in image on the sides

maxYOffset = 63
minYOffset = 77

y1 = 0
y2 = 0

def displayImg(screenshot):
    screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
    cv.imshow('screenshot', screenshot)
    cv.waitKey()
    cv.destroyAllWindows()

def getMiddle(screenshot, plusCords):
        middle = False
        j = 0
        for j in range(20):
            if np.allclose(screenshot[plusCords[0], plusCords[1] + j], plusColor, atol=10):
                for k in range(18):
                    if np.allclose(screenshot[plusCords[0] + k, plusCords[1] + j - 1], plusColor, atol=10):
                        middle = [plusCords[0] + k, plusCords[1] + j]
                        return middle

def getLeftItem(screenshot, middle, itemOffset):
    x1 = middle[1] - plusSideOffset * (itemOffset + 1) + plusArmOsset
    x2 = middle[1] - plusSideOffset * itemOffset - plusArmOsset
    return screenshot[y1:y2, x1:x2]

def getRightItem(screenshot, middle, itemOffset):
    x1 = middle[1] + plusSideOffset * itemOffset + plusArmOsset
    x2 = middle[1] + plusSideOffset * (itemOffset + 1) - plusArmOsset
    return screenshot[y1:y2, x1:x2]

def main():
    global y1, y2

    for i in range(20):
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)

        itemCount = 0
        middle = getMiddle(screenshot, centerPlus)
        if middle:
            plusToLeft = np.allclose(screenshot[middle[0], middle[1] + plusSideOffset], plusColor, atol=10)
            itemCount = 4 if plusToLeft else 2
        else:
            middle = getMiddle(screenshot, leftPlus)
            itemCount = 3

        if not middle:
            print(False)
            return

        y1 = middle[0] - minYOffset
        y2 = middle[0] + maxYOffset

        items = []
        if itemCount == 4:
            items.append(getLeftItem(screenshot, middle, 1))
            items.append(getLeftItem(screenshot, middle, 0))
            items.append(getRightItem(screenshot, middle, 0))
            items.append(getRightItem(screenshot, middle, 1))

        elif itemCount == 3:
            items.append(getLeftItem(screenshot, middle, 0))
            items.append(getRightItem(screenshot, middle, 0))
            items.append(getRightItem(screenshot, middle, 1))

        else:
            items.append(getLeftItem(screenshot, middle, 0))
            items.append(getRightItem(screenshot, middle, 0))

        for i in range(len(items)):
            cv.imwrite(f"item{i}.png", items[i])

        print(itemCount)
        return

main()
